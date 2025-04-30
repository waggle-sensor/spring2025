import pandas as pd
import json
import os
"""
This script combines two ground truth caption CSV files into a single JSON file.
Each image ID will have a list of two ground truth captions (one from each CSV),
formatted for use in multi-reference image captioning evaluation.

Inputs:
- CSV 1: Image IDs and captions (Batch1_ground_truths_1.csv)
- CSV 2: Image IDs and captions (Batch1_ground_truths_2.csv)

Output:
- JSON file: Combined references for each image ID (Batch1_combined_ground_truths.json)
"""
# ------------------ CONFIGURATION ------------------

# Path to the first ground truth CSV (Batch 1, Set 1)
GT1_CSV = "data/ground_truths/Batch1_ground_truths_1.csv"

# Path to the second ground truth CSV (Batch 1, Set 2)
GT2_CSV = "data/ground_truths/Batch1_ground_truths_2.csv"

# Output path for the combined ground truth JSON
OUTPUT_JSON = "data/ground_truths/Batch1_combined_ground_truths.json"

# ----------------------------------------------------

# Load both ground truth CSV files into pandas DataFrames
gt1 = pd.read_csv(GT1_CSV)
gt2 = pd.read_csv(GT2_CSV)

# ------------------ BUILD COMBINED REFERENCES ------------------

# Initialize an empty dictionary to store combined references
combined_references = {}

# Add captions from the first ground truth file
for _, row in gt1.iterrows():
    image_id = row['image_id']
    caption1 = row['ground_truth_caption']
    combined_references[image_id] = [caption1]  # Start a list with the first caption

# Add captions from the second ground truth file
for _, row in gt2.iterrows():
    image_id = row['image_id']
    caption2 = row['ground_truth_caption']
    if image_id in combined_references:
        combined_references[image_id].append(caption2)  # Append second caption if image already exists
    else:
        combined_references[image_id] = [caption2]  # Otherwise, create a new entry

# ------------------ SAVE COMBINED JSON ------------------

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

# Write the combined dictionary to a JSON file (pretty formatted with indent=2)
with open(OUTPUT_JSON, "w") as f:
    json.dump(combined_references, f, indent=2)

print(f"✅ Combined ground truth saved to '{OUTPUT_JSON}'")
