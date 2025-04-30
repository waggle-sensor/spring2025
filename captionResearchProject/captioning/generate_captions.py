"""
This script generates image captions by applying a selected vision-language model
(Gemma-3, Kosmos-2, etc.) to a batch of input images.
It saves the generated captions into a model-specific CSV file for further evaluation.

Inputs:
- CSV file listing image filenames to caption
- Selected captioning model (e.g., Gemma-3, Kosmos-2)
- Image files stored in a local directory

Outputs:
- CSV file containing filenames and their corresponding generated captions
"""

import os
import pandas as pd
from tqdm import tqdm

# ------------------ Configuration ------------------

# Path to folder where all input images are stored
IMAGES_DIR = "data/images/"

# Path to the CSV file listing which images to caption
INPUT_CSV = "data/images/sampled_images.csv"

# Set the model name you want to use
# Options: "gemma3", "kosmos2", etc.
MODEL_NAME = "gemma3"

# -----------------------------------------------------

# Set the model-specific output directory
# Captions will be saved in: data/model_captions/{MODEL_NAME}/{MODEL_NAME}_captions.csv
MODEL_OUTPUT_DIR = f"data/model_captions/{MODEL_NAME}/"
OUTPUT_CAPTIONS_FILE = os.path.join(MODEL_OUTPUT_DIR, f"{MODEL_NAME}_captions.csv")

# Create the output directory if it doesn't exist
os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

# Load the input CSV file containing image filenames
df = pd.read_csv(INPUT_CSV)

captions = []

# Loop through each image entry and generate a caption
for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"Generating captions with {MODEL_NAME}"):
    filename = row["filename"]
    image_path = os.path.join(IMAGES_DIR, filename)

    # Skip if the image file is missing
    if not os.path.exists(image_path):
        print(f"⚠️ Skipping missing file: {filename}")
        continue

    try:
        # Lazy import the model-specific caption generator
        # If you want to use a different model, change the import statement accordingly
        if MODEL_NAME == "gemma3":
            from models.gemma3 import generate_caption_gemma3
            caption = generate_caption_gemma3(image_path)
        elif MODEL_NAME == "kosmos2":
            from models.kosmos2 import generate_caption_kosmos2
            caption = generate_caption_kosmos2(image_path)
        else:
            raise ValueError(f"Unknown model: {MODEL_NAME}")

        # Only add non-empty captions
        if caption.strip():
            captions.append({
                "filename": filename,
                "caption": caption
            })
        else:
            print(f"⚠️ Empty caption for: {filename}")

    except Exception as e:
        print(f"❌ Error captioning {filename}: {e}")

# Save all generated captions to a CSV file
if captions:
    os.makedirs(os.path.dirname(OUTPUT_CAPTIONS_FILE), exist_ok=True)
    df_captions = pd.DataFrame(captions)
    df_captions.to_csv(OUTPUT_CAPTIONS_FILE, index=False)
    print(f"✅ Captions saved to '{OUTPUT_CAPTIONS_FILE}'.")
else:
    print("No captions generated.")
