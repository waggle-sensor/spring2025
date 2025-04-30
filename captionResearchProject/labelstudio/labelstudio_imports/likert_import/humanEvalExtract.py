"""
This script processes a human Likert-scale evaluation export from Label Studio.
It generates two outputs:
- A full list of image-level human evaluation scores
- A model-level breakdown showing how many 'Excellent', 'Good', etc. ratings each model received

Inputs:
- Label Studio export CSV containing image, model name, and human Likert rating

Outputs:
- Full evaluation scores CSV (image_id, model, human_score)
- Summary breakdown CSV (model name + count of each rating)
"""

import os
import pandas as pd

# ------------------ CONFIGURATION ------------------

# Path to the Label Studio export CSV (update if necessary)
INPUT_CSV = "labelstudio/labelstudio_imports/likert_import/project-13-at-2025-04-26-18-11-43d8e445.csv"

# Directory where cleaned evaluation data will be saved
OUTPUT_DIR = "data/metrics/human_evaluation/Batch1/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Output file paths
FULL_SCORES_FILE = os.path.join(OUTPUT_DIR, "human_batch1Urban_eval_scores.csv")
BREAKDOWN_FILE = os.path.join(OUTPUT_DIR, "human_batch1Urban_eval_breakdown.csv")

# Mapping human ratings (text) to numeric scores
rating_map = {
    "Bad": 1,
    "Poor": 2,
    "Fair": 3,
    "Good": 4,
    "Excellent": 5
}

# -----------------------------------------------------

# ------------------ LOAD AND PREPARE DATA ------------------

# Load the Label Studio export
df = pd.read_csv(INPUT_CSV)

# Map the Likert text ratings to numeric scores
df['human_score'] = df['rating'].map(rating_map)

# Extract clean image IDs from the 'image' field
df['image_id'] = df['image'].str.extract(r'/([^/]+\.jpg)')[0]  # Extract filename (e.g., "sample.jpg")
df['image_id'] = df['image_id'].str.replace('?d=', '', regex=False)  # Remove any leftover '?d='

# Ensure the 'model' field exists (required for breakdown)
if 'model' not in df.columns:
    raise ValueError("❗ Model field missing from Label Studio export! Check your import.")

# ------------------ SAVE FULL EVALUATION SCORES ------------------

# Save a clean CSV listing image_id, model, and human_score
df[['image_id', 'model', 'human_score']].to_csv(FULL_SCORES_FILE, index=False)
print(f"✅ Saved full evaluation scores to '{FULL_SCORES_FILE}'")

# ------------------ BUILD AND SAVE RATING BREAKDOWN ------------------

# Create a pivot table counting how many of each rating each model received
breakdown = df.pivot_table(
    index='model',
    columns='rating',
    aggfunc='size',
    fill_value=0
).reset_index()

# Enforce column order for consistency
ordered_cols = ['model', 'Excellent', 'Good', 'Fair', 'Poor', 'Bad']
for col in ordered_cols:
    if col not in breakdown.columns:
        breakdown[col] = 0  # Add missing columns if necessary
breakdown = breakdown[ordered_cols]

# Save the breakdown to CSV
breakdown.to_csv(BREAKDOWN_FILE, index=False)
print(f"✅ Saved rating breakdown to '{BREAKDOWN_FILE}'")
