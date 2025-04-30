"""
This script processes a human-annotated export from Label Studio to create a clean ground truth CSV.
It extracts the image IDs from file paths, renames fields for consistency, 
and outputs a simple CSV with image IDs and corresponding ground truth captions.

Inputs:
- Label Studio export CSV (containing image paths and human-written captions)

Outputs:
- Cleaned CSV mapping image IDs to ground truth captions (e.g., Batch1_ground_truths_2.csv)
"""

import pandas as pd
import os

# ------------------ CONFIGURATION ------------------

# Path to the Label Studio export CSV (update path if necessary)
GROUND_TRUTH_EXPORT = "labelstudio/labelstudio_imports/human_annotation_import/project-14-at-2025-04-26-17-53-4d701d9a.csv"

# Path where the cleaned ground truth CSV will be saved
OUTPUT_CSV = "data/ground_truths/Batch1_ground_truths_2.csv"

# -----------------------------------------------------

# ------------------ LOAD AND CLEAN DATA ------------------

# Load the exported CSV from Label Studio
df = pd.read_csv(GROUND_TRUTH_EXPORT)

# Identify the correct column that contains image file information
# (it may be labeled 'captioning' or 'image' depending on the project)
if 'captioning' in df.columns:
    image_column = 'captioning'
elif 'image' in df.columns:
    image_column = 'image'
else:
    raise ValueError("Cannot find image column ('captioning' or 'image') in the export!")

# Extract only the filename (e.g., "sample.jpg") from full paths or URLs
df['image_id'] = df[image_column].str.extract(r'-([^/]+\.jpg)')[0]

# Rename the human-written caption column to 'ground_truth_caption'
if 'caption' in df.columns:
    df = df.rename(columns={"caption": "ground_truth_caption"})
else:
    raise ValueError("Cannot find 'caption' field in export!")

# Keep only the necessary columns for downstream evaluation
df = df[['image_id', 'ground_truth_caption']]

# ------------------ SAVE CLEANED CSV ------------------

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# Save the cleaned DataFrame to CSV
df.to_csv(OUTPUT_CSV, index=False)

print(f"✅ Clean ground truth CSV saved to '{OUTPUT_CSV}'")
