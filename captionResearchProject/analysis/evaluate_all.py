"""
This script evaluates model-generated image captions against ground truth captions using multiple metrics.
It calculates BLEU, ROUGE, METEOR, BERTScore, and CLIPScore for each model and saves the aggregated results.

Inputs:
- Ground truth captions (JSON file with multiple references per image)
- Model-generated captions (CSV files, one per model)
- Original input images (for CLIPScore calculation)

Outputs:
- CSV file summarizing evaluation scores per model

Metrics computed:
- BLEU-1, BLEU-2, BLEU-3, BLEU-4
- ROUGE-1, ROUGE-2, ROUGE-L
- METEOR
- Average CLIPScore
- Average BERTScore F1
"""


import os
import json
import csv
import nltk
import torch
import evaluate
import open_clip
import pandas as pd
from PIL import Image
from tqdm import tqdm
from bert_score import score

# ------------------ CONFIGURATION ------------------

# Path to ground truth captions
GROUND_TRUTH_JSON = "data/ground_truths/Batch1_combined_ground_truths.json"

# Directory containing all model-generated captions (each model in its own folder)
MODEL_OUTPUT_DIR = "data/model_captions/"

# Directory containing the original input images
IMAGES_DIR = "data/images"

# Path to save the final CSV with evaluation scores
OUTPUT_CSV = "data/metrics/evaluated/Batch1_full_evaluation_scores.csv"

# Settings for loading the CLIP model
CLIP_MODEL_NAME = "ViT-B-32"
CLIP_PRETRAINED = "openai"

# Automatically detect whether to use GPU ('cuda') or CPU ('cpu')
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# ----------------------------------------------------

# Download required NLTK datasets (quiet=True to suppress download output)
nltk.download("wordnet", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("omw-1.4", quiet=True)

# Load Ground Truth annotations
with open(GROUND_TRUTH_JSON, "r") as f:
    ground_truths = json.load(f)

# Load evaluation metrics (BLEU, ROUGE, METEOR) from Hugging Face Evaluate
bleu = evaluate.load("bleu")
rouge = evaluate.load("rouge")
meteor = evaluate.load("meteor")

# Load CLIP model and preprocessing transforms
print("⏳ Loading CLIP model...")
clip_model, _, clip_transform = open_clip.create_model_and_transforms(CLIP_MODEL_NAME, pretrained=CLIP_PRETRAINED)
clip_tokenizer = open_clip.get_tokenizer(CLIP_MODEL_NAME)
clip_model.to(DEVICE)
print("✅ CLIP model loaded.")

# ------------------ HELPER FUNCTIONS ------------------

# Helper to recursively round all float values (for saving nicely formatted results)
def round_values(data, precision=4):
    if isinstance(data, dict):
        return {k: round_values(v, precision) for k, v in data.items()}
    elif isinstance(data, list):
        return [round_values(v, precision) for v in data]
    elif isinstance(data, (int, float)):
        return round(data, precision)
    else:
        return data

# Helper to compute CLIPScore between an image and a generated caption
def compute_clipscore(image_path, caption):
    try:
        image = Image.open(image_path).convert("RGB")
        image_input = clip_transform(image).unsqueeze(0).to(DEVICE)
        text_input = clip_tokenizer([caption]).to(DEVICE)
        with torch.no_grad():
            image_features = clip_model.encode_image(image_input)
            text_features = clip_model.encode_text(text_input)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        clip_score = 2.5 * (image_features @ text_features.T).item()
        return clip_score
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

# Helper to compute best BERTScore (when multiple references are available)
def compute_best_bertscore(candidate, references):
    max_f1, max_p, max_r = 0, 0, 0
    for ref in references:
        P, R, F1 = score([candidate], [ref], lang='en', rescale_with_baseline=True, verbose=False)
        f1 = F1.mean().item()
        if f1 > max_f1:
            max_f1 = f1
            max_p = P.mean().item()
            max_r = R.mean().item()
    return max_p, max_r, max_f1

# ------------------ MAIN EVALUATION LOOP ------------------

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# Open CSV file to write evaluation scores
with open(OUTPUT_CSV, "w", newline="") as csvfile:
    fieldnames = [
        "model_name", "bleu", "bleu1", "bleu2", "bleu3", "bleu4",
        "rouge1", "rouge2", "rougeL", "meteor", "average_clip_score", "bert_f1"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Find all model caption CSV files
    model_files = []
    for root, dirs, files in os.walk(MODEL_OUTPUT_DIR):
        for file in files:
            if file.endswith("_captions.csv"):
                model_files.append(os.path.join(root, file))

    # Loop over each model's captions and compute metrics
    for model_file in model_files:
        print(f"\n🔎 Processing {model_file}...")
        model_name = os.path.basename(model_file).replace("_captions.csv", "")

        # Load model-generated captions
        df = pd.read_csv(model_file)
        predictions = {row['filename']: row['caption'] for _, row in df.iterrows()}

        # Only evaluate on images that exist in both ground truth and predictions
        image_ids = set(ground_truths.keys()) & set(predictions.keys())

        formatted_predictions = [predictions[iid] for iid in image_ids]
        formatted_references = [ground_truths[iid] for iid in image_ids]

        # --- BLEU, ROUGE, METEOR ---
        bleu_result = bleu.compute(predictions=formatted_predictions, references=formatted_references)
        rouge_result = rouge.compute(predictions=formatted_predictions, references=formatted_references)
        meteor_result = meteor.compute(predictions=formatted_predictions, references=formatted_references)

        # --- CLIPScore ---
        total_clip = 0
        clip_count = 0
        for iid in tqdm(image_ids, desc=f"CLIPScore {model_name}"):
            file_name = iid  # assuming image filename matches image_id
            image_path = os.path.join(IMAGES_DIR, file_name)
            if os.path.exists(image_path):
                clip_score = compute_clipscore(image_path, predictions[iid])
                if clip_score is not None:
                    total_clip += clip_score
                    clip_count += 1
            else:
                print(f"⚠️ Missing image {image_path}")

        avg_clip_score = total_clip / clip_count if clip_count > 0 else 0

        # --- BERTScore ---
        bert_scores = []
        for iid in tqdm(image_ids, desc=f"BERTScore {model_name}"):
            pred = predictions[iid]
            refs = ground_truths[iid]
            _, _, f1 = compute_best_bertscore(pred, refs)
            bert_scores.append(f1)
        avg_bert_f1 = sum(bert_scores) / len(bert_scores) if bert_scores else 0

        # Save final row with all metrics to CSV
        row = {
            "model_name": model_name,
            "bleu": round(bleu_result["bleu"], 4),
            "bleu1": round(bleu_result["precisions"][0], 4),
            "bleu2": round(bleu_result["precisions"][1], 4),
            "bleu3": round(bleu_result["precisions"][2], 4),
            "bleu4": round(bleu_result["precisions"][3], 4),
            "rouge1": round(rouge_result["rouge1"], 4),
            "rouge2": round(rouge_result["rouge2"], 4),
            "rougeL": round(rouge_result["rougeL"], 4),
            "meteor": round(meteor_result["meteor"], 4),
            "average_clip_score": round(avg_clip_score, 4),
            "bert_f1": round(avg_bert_f1, 4)
        }
        writer.writerow(row)

print(f"\n✅ Full evaluation results saved to {OUTPUT_CSV}")
