## 📜 Script Overview

| Script | Purpose | Inputs | Outputs |
|:------|:--------|:-------|:--------|
| **generate_captions.py** | Generates captions for a batch of images using a specified model (e.g., Gemma-3, Kosmos-2). | Image files, Image filenames CSV, Selected model name | CSV file with generated captions |
| **evaluate_captions.py** | Evaluates generated captions against ground truth using BLEU, ROUGE, METEOR, BERTScore, and CLIPScore. | Ground truth JSON, Generated captions CSVs, Image files | Evaluation scores CSV |
| **gemma3_captioner.py** | Loads the Gemma-3 model and generates a paragraph-style caption for a single input image. | Image path | Generated caption (string) |
| **kosmos2_captioner.py** | Loads the Kosmos-2 model and generates a cleaned two-sentence caption for a single input image. | Image path | Generated caption (string) |
| **prepare_labelstudio_import.py** | Prepares a CSV for importing generated captions into Label Studio for human evaluation. | Model-generated captions CSV | Formatted Label Studio import CSV |
| **process_human_annotations.py** | Cleans a Label Studio export of human ground-truth captions for evaluation. | Label Studio export CSV | Cleaned ground truth CSV |
| **combine_ground_truths.py** | Combines two ground truth CSVs into a single JSON file with multiple references per image. | Two ground truth CSVs | Combined ground truth JSON |
| **process_likert_ratings.py** | Processes human Likert ratings from Label Studio into full scores and a breakdown by model. | Label Studio export CSV (Likert ratings) | Full human evaluation scores CSV + Model rating breakdown CSV |
| **download_sample_images.py** | Downloads a sample of images from Sage nodes based on a time range and saves metadata. | Sage credentials, Node IDs, Time range | Downloaded images + Sampled images metadata CSV |


# 🧭 User Guide

## 1. Project Folder Structure

```plaintext
caption_project/
├── analysis/
│   └── evaluate_all.py
│
├── captioning/
│   ├── models/
│   │   ├── gemma3.py
│   │   └── kosmos2.py
│   └── evaluate.py
│
├── data/
│   ├── ground_truths/
│   │   └── combine_truths.py
│   ├── images/
│   ├── metrics/
│   │   ├── evaluated/
│   │   └── human_evaluation/
│   └── model_captions/
│       ├── gemma3/
│       └── kosmos2/
│
├── download/
│   └── download_images.py
│
├── labelstudio/
│   ├── labelstudio_exports/
│   │   ├── annotate_config/
│   │   │   └── annotate.txt    # Label Studio UI annotation setup
│   │   ├── export_csv/
│   │   └── likert_config/
│   │       └── label_config_setup.txt    # Label Studio UI evaluation setup
│   ├── prepare_for_labelstudio.py
│   └── labelstudio_imports/
│       ├── human_annotations_import/
│       │   └── clean_imports.py
│       └── likert_import/
│           └── humanEvalExtract.py
│
├── venv/                      # Python virtual environment
```
## 2. 📦 Setup Instructions

- Install Python 3.10 or higher.
- Install required libraries:
  ```bash
  pip install -r requirements.txt
  ```
## 3. 🔐 Setting Sage Credentials

Before downloading images from Sage nodes, you must set your Sage API credentials as environment variables.

You can set them in your terminal session like this:

```bash
export SAGE_USER=your_username
export SAGE_TOKEN=your_token
```

## 4. 🚀 Step-by-Step Workflow

Follow these steps to run the full project pipeline:


### Step 4.1 — Download Images

Download a batch of images from Sage nodes:

```bash
python download/download_images.py
```

This will:
- Download images into specified path and create a sample_images.csv file listing in the image folder.
- Save the images into the folder: data/images/
- Create a metadata file listing all downloaded images: data/images/sampled_images.csv

### Step 4.2 — Generate Captions

Use a model (e.g., Gemma-3 or Kosmos-2) to generate captions for the downloaded images:

```bash
python captioning/generate_captions.py
```

This will:
- Read the list of images from: data/images/sampled_images.csv
- Generate a caption for each image using the selected model (set inside the script)
- Save the generated captions into: data/model_captions/{model_name}/{model_name}_captions.csv

### Step 4.3 — Start Label Studio to Annotate Images (Ground Truth Creation)

Start Label Studio correctly by serving images from the local directory:

```bash
LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true \
LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=$(pwd)/data/images \
label-studio
```

This will:
- Serve your `data/images/` folder locally
- Start Label Studio at: http://localhost:8080

In Label Studio:
- Create a new annotation project
- Import the images from `data/images/`
- Set the Labelling Configuration using `annotate.txt` code
- Write a ground-truth caption for each image

After completing annotation:
- Export your annotations as a CSV file
- This file will be used later to evaluate model performance


### Step 4.4 — Combine Ground Truth Captions (if using two batches)

If you have two separate ground truth annotation files (for example, from two different annotators), you need to combine them into a single file for evaluation.

Run the following script:

```bash
python data/ground_truths/combine_truths.py
```

This will:
- Read two CSV files containing ground-truth captions
- Merge them into a single JSON file with multiple references per image for more accurate evaluation
- The combined ground truth file will be saved at: data/ground_truths/Batch1_combined_ground_truths.json


### Step 4.5 (Optional Unless Performing Likert Eval) — Prepare Model Captions for Human Evaluation

Before starting human evaluation, you must prepare the model-generated captions for import into Label Studio.

Run the script:

```bash
python labelstudio/prepare_for_labelstudio.py
```

This script:
- Adds a full 'image' path expected by Label Studio '/data/local-files/?d=filename.jpg'
- Adds a 'model' column to identify which model generated each caption
- Saves a new CSV file ready for import into Label Studio
- You must run this script once for each model you plan to evaluate (e.g., Gemma-3, Kosmos-2)
- Saved to: labelstudio/labelstudio_exports/export_csv/{model_name}_labelstudio.csv

### Step 4.6 (Optional Unless Performing Likert Eval) — Perform Human Evaluation of Model Captions

Once you have prepared the model caption files (see Step 4.5), you can set up human evaluation using Label Studio.

Start Label Studio by serving your local image files:

```bash
LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true \
LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=$(pwd)/data/images \
label-studio
```

This will:
- Serve your data/images/ folder locally
- Start Label Studio at http://localhost:8080

**In Label Studio:**

1. **Create a New Project**
   - Click **Create Project**.
   - Enter a project name (e.g., "Model Caption Evaluation").

2. **Upload Formatted Model Captions**
   - Go to the **Tasks** tab → Click **Import**.
   - Upload the prepared model caption CSV(s) from Step 4.5:
     - Examples: `kosmos2_labelstudio.csv`, `gemma3_labelstudio.csv`.
   - Confirm that the tasks appear correctly and the image paths use `/data/local-files/?d=...`.

3. **Set Up the Labeling Interface**
   - Go to **Settings → Labeling Interface**.
   - Open the file:

     ```plaintext
     labelstudio/labelstudio_exports/likert_config/label_config_setup.txt
     ```

   - Copy the contents of that file.
   - Paste it into the Labeling Interface editor.
   - Save the configuration.

4. **Connect to Image Storage**
   - Go to **Cloud Storage** inside your project settings.
   - Click **Add Source Storage**.
   - Choose **Local Files** as the storage type.
   - Set the **Storage Title** (e.g., "Local Images").
   - Set the **Absolute Path** to your images folder:

     ```plaintext
     /path/to/caption_project/data/images
     ```

   - Set the **File Filter Regex** to:

     ```plaintext
     .*\.jpg$
     ```

   - Click **Check Connection** to verify Label Studio can access the images.
   - **Important:** Make sure you **DO NOT sync** the storage — just connect it.

5. **Begin Human Evaluation**
   - Start reviewing each image and caption pair.
   - Assign a rating using the Likert scale: **Excellent**, **Good**, **Fair**, **Poor**, or **Bad**.

### Step 4.7 (Optional Unless Performing Likert Eval) — Process Human Ratings

After exporting the human evaluation results from Label Studio as a csv, you need to process the ratings to create clean CSV files for analysis.

Make sure the exported human ratings CSV is placed in the correct folder: labelstudio/labelstudio_imports/likert_import/

Run the following script:

```bash
python labelstudio/labelstudio_imports/likert_import/humanEvalExtract.py
```

This will:
- Extract the image ID, model name, and human rating from the Label Studio export.
- Save two output files: full evaluation of scores and a breakdown

### Step 4.8 — Automatically Evaluate Model Captions

Now that you have:
- Combined ground truth captions (human-annotated references)
- Generated model captions

You can automatically evaluate the model captions against the ground truths using multiple standard metrics.

Run the evaluation script:

```bash
python analysis/evaluate_all.py
```

This script will:
- Load model-generated captions from: data/model_captions/{model_name}/{model_name}_captions.csv
- Load ground truth captions from: data/ground_truths/Batch1_combined_ground_truths.json
- Complete eval metrics

---

## ✅ End of Workflow

After completing Step 4.8, you will have:

- Human evaluation results (optional):
  - Full human scores CSV
  - Human rating breakdown summary

- Automatic evaluation results:
  - Full metrics (BLEU, ROUGE, METEOR, BERTScore, CLIPScore) for each model

You can now analyze model performance both quantitatively and qualitatively to determine which model generates the best captions for your dataset.

---
