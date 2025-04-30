"""
This script loads the Gemma-3 12B vision-language model and generates captions for input images.
It formats an image into a chat-style prompt, runs inference, and decodes the generated text output.

Inputs:
- Path to an input image file

Outputs:
- Caption describing the image content.

Usage:
- Import and call generate_caption_gemma3(image_path) from another script
- (Optional) Run standalone from command line if __main__ block is uncommented
"""

# ------------------ GEMMA3 CAPTIONING SCRIPT ------------------
from transformers import AutoProcessor, Gemma3ForConditionalGeneration
import torch

# ------------------ DEVICE SETUP ------------------

# Select device:
# Use Apple MPS (Metal Performance Shaders) if available (for Mac GPUs),
# otherwise fallback to CPU.
device = "mps" if torch.backends.mps.is_available() else "cpu"

# ------------------ MODEL CONFIGURATION ------------------

# Hugging Face model ID for the Gemma 3-12B instruction-tuned model
model_id = "google/gemma-3-12b-it"

# Load the pre-trained Gemma3 model
print("⏳ Loading Gemma3 model...")
model = Gemma3ForConditionalGeneration.from_pretrained(
    model_id,
    device_map=device,          # Map model to the detected device
    torch_dtype=torch.bfloat16  # Use bfloat16 for faster/lower-memory inference
).to(device).eval()             # Move to device and set to evaluation mode

# Load the corresponding processor (handles both images and text)
processor = AutoProcessor.from_pretrained(model_id, use_fast=True)
print("✅ Gemma3 model loaded.")

# ------------------ CAPTION GENERATION FUNCTION ------------------

def generate_caption_gemma3(image_path):
    """
    Generates a caption for the given image using the Gemma3 model.

    Args:
        image_path (str): Path to the input image.

    Returns:
        str: Generated caption text.
    """
    try:
        # Define the chat prompt template for the model
        messages = [
            {"role": "system", "content": [{"type": "text", "text": "You are an image captioner."}]},
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_path},
                    {"type": "text", "text": "Describe the main contents of this image objectively in paragraph format."}
                ]
            }
        ]

        # Preprocess image + text into model input format
        inputs = processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(model.device, dtype=torch.bfloat16)

        # Track the length of the input to separate generated output later
        input_len = inputs["input_ids"].shape[-1]

        # Generate caption using the model (no gradient tracking needed)
        with torch.inference_mode():
            generation = model.generate(**inputs, max_new_tokens=200)
            generation = generation[0][input_len:]  # Remove input tokens from output

        # Decode output tokens into readable text
        caption = processor.decode(generation, skip_special_tokens=True)

        # 🧼 Clean-up: Remove preface text if there are double newlines
        if "\n\n" in caption:
            caption = caption.split("\n\n", 1)[-1].strip()

        return caption

    except Exception as e:
        print(f"❌ Gemma3 error on {image_path}: {e}")
        return ""

# ------------------ COMMAND LINE EXECUTION ------------------

# Allow running this script standalone
"""
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gemma_captioner.py path/to/image.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    result = generate_caption_gemma3(image_path)
    print("\n🖼️ Caption:\n", result)
"""

