"""
This script loads the Kosmos-2 vision-language model and generates captions for input images.
It feeds an image and a fixed prompt into the model, generates a detailed description,
and cleans the output to remove artifacts and standardize formatting.

Inputs:
- Path to an input image file

Outputs:
- Cleaned, objective caption describing the scene.

Usage:
- Import and call generate_caption_kosmos2(image_path) from another script
"""


from transformers import AutoProcessor, Kosmos2ForConditionalGeneration
from PIL import Image
import torch
import re

# ------------------ MODEL INFO ------------------

# Kosmos-2 Model Information:
# Model: microsoft/kosmos-2-patch14-224

# ------------------ DEVICE SETUP ------------------

# Set device priority:
# 1. Prefer CUDA (NVIDIA GPU)
# 2. Else prefer MPS (Apple Silicon GPU)
# 3. Else fallback to CPU
if torch.cuda.is_available():
    device = "cuda"
    torch_dtype = torch.float16
elif torch.backends.mps.is_available():
    device = "mps"
    torch_dtype = torch.float16
else:
    device = "cpu"
    torch_dtype = torch.float32

# ------------------ MODEL LOADING ------------------

# Load the Kosmos-2 model onto the selected device
kosmos_model = Kosmos2ForConditionalGeneration.from_pretrained(
    "microsoft/kosmos-2-patch14-224",
    torch_dtype=torch_dtype,
    device_map="auto"  # Automatically map across available hardware
).to(device).eval()   # Set to evaluation mode (no gradients)

# Load the Kosmos-2 processor (handles both text and image inputs)
kosmos_processor = AutoProcessor.from_pretrained("microsoft/kosmos-2-patch14-224")

# ------------------ CAPTION GENERATION FUNCTION ------------------

def generate_caption_kosmos2(image_path):
    """
    Generates a caption for the given image using the Kosmos-2 model.

    Args:
        image_path (str): Path to the input image.

    Returns:
        str: Cleaned, objective caption text.
    """
    try:
        # Load and preprocess the input image
        image = Image.open(image_path).convert("RGB")
        prompt = "Describe the scene objectively in detail:"

        # Tokenize text + image inputs
        inputs = kosmos_processor(text=prompt, images=image, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}

        # Generate caption (disable gradient computation for efficiency)
        with torch.inference_mode():
            generated_ids = kosmos_model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=False 
            )
            decoded_caption = kosmos_processor.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]

        # ------------------ CLEAN-UP ------------------

        # 1. Remove any leftover <image> tags
        cleaned = re.sub(r"<\/?image>", "", decoded_caption)

        # 2. Remove any repeated prompts or irrelevant preface text
        match = re.search(r"(describe the scene.*?)[:\-]", cleaned, re.IGNORECASE)
        if match:
            start_idx = match.end()
            cleaned = cleaned[start_idx:].strip()
        else:
            # Fallback: Strip any leading non-letter characters
            cleaned = re.sub(r"^[^A-Za-z]+", "", cleaned)

        # 3. Fix common Unicode artifacts (smart quotes, apostrophes)
        cleaned = cleaned.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
        cleaned = cleaned.strip()

        # 4. Truncate output to a maximum of two sentences
        sentences = cleaned.split(". ")
        cleaned = ". ".join(sentences[:2]).strip()
        if not cleaned.endswith("."):
            cleaned += "."

        return cleaned

    except Exception as e:
        print(f"❌ Kosmos2 error for {image_path}: {e}")
        return ""
