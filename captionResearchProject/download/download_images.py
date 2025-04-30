"""
This script downloads a sample of images from Sage nodes within a specified time window.
It queries the Sage database for images, downloads a specified number of images per node,
and saves a CSV listing the filenames and original URLs.

Inputs:
- Node IDs (e.g., W040, etc.)
- Start and End timestamps
- Sage credentials (SAGE_USER and SAGE_TOKEN environment variables)

Outputs:
- Downloaded images saved locally
- A CSV file listing sampled images and their URLs (sampled_images.csv)
"""

import os
import pandas as pd
import requests
import sage_data_client

# ------------------ CONFIGURATION ------------------

# Time window for querying images
START = "2025-04-26T00:00:00Z"
END = "2025-04-26T23:59:59Z"

# List of node IDs to sample from
NODES = [ 
    "W040"
]

# Directory to save downloaded images
IMAGES_DIR = "data/images/"

# Output CSV file for sampled image metadata
SAMPLED_IMAGES_CSV = "data/images/sampled_images.csv"

# Number of images to sample per node
SAMPLES_PER_NODE = 4

# -----------------------------------------------------

# ------------------ AUTHENTICATION ------------------

# Load Sage API credentials from environment variables
USER = os.getenv("SAGE_USER")
TOKEN = os.getenv("SAGE_TOKEN")
if not USER or not TOKEN:
    raise EnvironmentError("SAGE_USER and/or SAGE_TOKEN are not set.")

# ------------------ PREPARE OUTPUT DIRECTORY ------------------

# Create the image directory if it does not exist
os.makedirs(IMAGES_DIR, exist_ok=True)

# Initialize list to collect sampled image metadata
all_sampled = []

# ------------------ QUERY AND DOWNLOAD IMAGES ------------------

for node in NODES:
    print(f"Querying data for node {node}...")
    
    # Query Sage database for images within the specified time window
    df = sage_data_client.query(
        start=START,
        end=END,
        filter={
            "vsn": node,
            "task": "imagesampler-.*"  # Filter to image sampling tasks
        }
    )

    if df.empty:
        print(f"No image data found for {node}.")
        continue

    # Convert timestamps to pandas datetime objects
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Randomly sample images (up to SAMPLES_PER_NODE)
    sampled_df = df.sample(n=min(SAMPLES_PER_NODE, len(df)), random_state=42)

    for _, row in sampled_df.iterrows():
        image_url = row["value"]
        original_filename = image_url.split("/")[-1]  # Extract filename from URL

        save_path = os.path.join(IMAGES_DIR, original_filename)

        try:
            # Download image with HTTP Basic Authentication
            response = requests.get(image_url, auth=(USER, TOKEN))
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded: {original_filename}")

                # Record metadata for the downloaded image
                all_sampled.append({
                    "filename": original_filename,
                    "image_url": image_url
                })

            else:
                print(f"Failed to download {image_url}: {response.status_code}")

        except Exception as e:
            print(f"Error downloading {image_url}: {e}")

# ------------------ SAVE SAMPLED METADATA ------------------

# If any images were downloaded, save metadata to CSV
if all_sampled:
    df_all = pd.DataFrame(all_sampled)
    df_all.to_csv(SAMPLED_IMAGES_CSV, index=False)
    print(f"✅ Metadata saved to '{SAMPLED_IMAGES_CSV}'.")
else:
    print("No images were downloaded.")
