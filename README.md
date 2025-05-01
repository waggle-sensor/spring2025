# spring2025

## Spring 2025 Programs

This repository contains two related projects developed in Spring 2025 focused on evaluating and generating image captions using large vision-language models.

---

## 📁 Projects

### 1. `captionResearchProject/`

A research-driven pipeline for evaluating AI-generated image captions.  
It includes tools to:

- Generate image captions using local models (e.g., Gemma, Kosmos-2)
- Convert outputs to standardized JSON/CSV formats
- Evaluate caption quality using:
  - BLEU, ROUGE, METEOR
  - BERTScore
  - CLIPScore
- Visualize and compare model performance across datasets (e.g., urban vs. rural)

This project was developed for internal analysis and academic poster presentation.

---

### 2. `codeCaptionGenerator/`

A lightweight Dockerized Python tool for generating image captions using vision-language models served via [Ollama](https://ollama.com).  
Supports models like:

- `llava:latest`
- `llama3.2-vision:90b`

Captions are generated via the Ollama REST API and exported to CSV.

✔️ **The output CSVs from this program are already in the format required by `captionResearchProject`, making them directly compatible for evaluation.**

---

## 📚 Reference Captions

The `referenceCaptions/` directory contains multiple sets of manually written ground truth captions for each evaluation batch (urban and rural). Each batch has two independently written reference sets to reduce bias in metric evaluation.

All files are in COCO-style JSON format, with fields including:
- `images`: metadata about each image (filename, dimensions, timestamp, etc.)
- `annotations`: human-written captions, each linked to an `image_id`
- Optional `labels`: keywords or concepts associated with the caption (used for exploratory purposes)

---

## captionCorrection

The `captionCorrection/` directory contains caption pairs consisting of a model's output caption and a human evaluated/corrected version of the model's output. In addition, there are metric evaluations of the improvements.

--

## 🧪 Status

Both tools are functional and were used in real evaluation pipelines.  
You may need to adjust image paths, model names, or mounts depending on your system setup.
