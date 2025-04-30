"""
This script prepares a CSV for uploading model-generated captions into Label Studio.
It modifies the original captions CSV by:
- Building the full 'image' path required by Label Studio based on real folder structure
- Adding a 'model' column to identify the source model
- Saving the formatted CSV into the Label Studio project directory.

Inputs:
- Model-generated captions CSV (e.g., kosmos2_captions.csv)

Outputs:
- Formatted CSV ready for Label Studio import (e.g., kosmos2_labelstudio.csv)
"""

import os
import pandas as pd

# ------------------ CONFIGURATION ------------------

# Model name (used for input and output file paths)
MODEL_NAME = "kosmos2"  # <-- Set this to the model you used

# Path to the model's original caption file
INPUT_CAPTIONS_FILE = f"data/model_captions/{MODEL_NAME}/{MODEL_NAME}_captions.csv"

# Output CSV path for Label Studio imports
OUTPUT_CSV_FOR_LS = f"labelstudio/labelstudio_exports/export_csv/{MODEL_NAME}_labelstudio.csv"

# Relative path inside Label Studio where the images are located
# (relative to DOCUMENT_ROOT, and matching the Label Studio accessible path)
IMAGE_RELATIVE_PATH = "data/images"  # <-- Adjust if your images are elsewhere

# Prefix Label Studio expects
IMAGE_DATA_PREFIX = "/data/local-files/?d="

# -----------------------------------------------------

# ------------------ LOAD AND FORMAT DATA ------------------

# Load model captions from CSV
df = pd.read_csv(INPUT_CAPTIONS_FILE)

# Create 'image' column by prepending Label Studio's expected prefix + relative path + filename
df["image"] = IMAGE_DATA_PREFIX + f"{IMAGE_RELATIVE_PATH}/" + df["filename"]

# Add a 'model' column for tracking model source during evaluation
df["model"] = MODEL_NAME

# Reorder columns for easier mapping inside Label Studio
df = df[["image", "caption", "model"]]

# ------------------ SAVE FORMATTED CSV ------------------

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUTPUT_CSV_FOR_LS), exist_ok=True)

# Save the new formatted CSV
df.to_csv(OUTPUT_CSV_FOR_LS, index=False)

print(f"✅ Label Studio CSV with 'model' saved to '{OUTPUT_CSV_FOR_LS}'.")
