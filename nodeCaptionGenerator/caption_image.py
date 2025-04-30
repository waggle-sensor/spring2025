import pandas as pd
import csv
import requests
import json
import os
import base64
import sys
import time
from datetime import datetime

# -------------------- Configuration --------------------
MODEL = "llava:latest"  # <-- set your model manually here

# Choose API endpoint based on model name
if any(key in MODEL for key in ["llama3.2", "gemma3"]):
    OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"
    is_chat_model = True
else:
    OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
    is_chat_model = False

# Folder of images
IMAGE_FOLDER = "example_images/images"  # <-- folder containing your images

# Output directory
OUTPUT_DIR = "captions_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Prompt
if MODEL == "llava:latest":
    PROMPT = (
    "[INST] <image>\nDescribe what you see in the image. [/INST]" # this is the prompt payload format for llava:latest, if using another generator model, adjust accordingly
    )
elif MODEL == "llama3.2-vision:90b":
    PROMPT = ( "<|begin_of_text|><|image|>" +
    "In a short paragraph, describe what you see in the image." +
    "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    )
else:
    PROMPT = (
        "Describe the main content of the image in a short paragraph."  
    )

# Collect all captions
all_captions = []

# List all image files
image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
image_files.sort()

for image_name in image_files:
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    try:
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()
        encoded_image = base64.b64encode(image_data).decode("utf-8")
    except Exception as e:
        print(f"❌ Failed to read image {image_name}: {e}")
        continue

    headers = {"Content-Type": "application/json"}

    if is_chat_model:
        payload = {
            "model": MODEL,
            "stream": False,
            "prompt": PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": ( PROMPT
                    ),
                    "images": [encoded_image]
                }
            ],
            "max_tokens": 50,
	    "temperature": .1
        }
    else:
        payload = {
            "model": MODEL,
            "prompt": PROMPT,
            "images": [encoded_image],
            "stream": False,
            "max_tokens": 50
        }

    try:
        start_time = time.time()
        response = requests.post(OLLAMA_ENDPOINT, headers=headers, data=json.dumps(payload), timeout=300)
        result = response.json()

        if 'message' in result and isinstance(result['message'], dict):
            output = result['message'].get('content', '')
        elif 'choices' in result and isinstance(result['choices'], list):
            output = result['choices'][0].get('message', {}).get('content', '')
        elif 'response' in result:
            output = result['response']
        else:
            output = json.dumps(result)

        end_time = time.time()
        duration = round(end_time - start_time, 2)

        print(f"✅ Captioned {image_name} in {duration}s")
        print(f"Capiton: {output.strip()}\n")
        all_captions.append({
            "image": image_name,
            "caption": output.strip(),
            "duration_sec": duration
        })

    except Exception as e:
        print(f"❌ Failed to caption image {image_name}: {e}")

# -------------------- Save all captions --------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

output_file = os.path.join(OUTPUT_DIR, f"{MODEL.replace('/', '_')}_{timestamp}_captions.csv")

# Use pandas to save CSV like your local scripts
df = pd.DataFrame([{
    "filename": entry["image"],
    "caption": entry["caption"].replace('\n', ' ')
} for entry in all_captions])

df.to_csv(output_file, index=False)
print(f"✅ Captions saved as CSV to: {output_file}")

