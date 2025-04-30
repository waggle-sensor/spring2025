# 🖼️ Caption Image Generator (Ollama + Python)

This script generates image captions using vision-language models hosted via [Ollama](https://ollama.com), such as `llava:latest` or `llama3.2-vision:90b`. The captions are saved as a clean CSV file for further evaluation or downstream use.

---

## 🚀 What It Does

- Takes a folder of images (JPG, PNG, BMP)
- Encodes each image in base64
- Sends it to the selected Ollama model via HTTP API
- Receives and logs a caption per image
- Saves results to a timestamped CSV in `captions_output/`

---

## 📦 Requirements

- Ollama running locally or on a node
- Python 3.8+
- `pandas`, `requests`

Install Python dependencies:

```bash
pip install pandas requests
```

---

## 🛠️ Configuration

Open `caption_image.py` and set the following:

```python
# Set the model to use (must be installed via Ollama)
MODEL = "llava:latest"  # Options tested include: "llava:latest", "llama3.2-vision:90b"

# Directory containing the input images
IMAGE_FOLDER = "images/"

# Directory where caption CSVs will be saved
OUTPUT_DIR = "captions_output"
```

Prompt format is automatically selected based on the model name:

| Model                  | Prompt Format |
|-----------------------|---------------|
| `llava:latest`        | `[INST] <image>\nDescribe what you see in the image. [/INST]` |
| `llama3.2-vision:90b` | `<|begin_of_text|><|image|>Describe the main contents of the image.<|eot_id|><|start_header_id|>assistant<|end_header_id|>` |
| Other / default       | `Describe the main content of the image in a short paragraph.` |

---

## 🧪 Example Output CSV

```csv
filename,caption
20240411_150009_nan_W01E_sample.jpg,"A chain-link fence with barbed wire and a warning sign."
20240409_210012_nan_W02D_sample.jpg,"A green mesh fence in front of a building under a clear sky."
```

---

## 🐳 Run with Docker (Optional)

### Dockerfile

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY caption_image.py .
COPY images/ images/
RUN pip install --no-cache-dir pandas requests
CMD ["python", "caption_image.py"]
```

### Build & Run

```bash
docker build -t caption-bot:latest .
docker run -ti --rm --runtime=nvidia --gpus all --shm-size 450G \
  --name captionbot --network host \
  -v /tmp/out:/app/captions_output \
  caption-bot:latest
```

Captions will be saved in `/tmp/out` on the host.

---

## 📁 Output Location

Saved to:

```
captions_output/MODELNAME_YYYYMMDD_HHMMSS_captions.csv
```

