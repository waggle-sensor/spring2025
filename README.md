# spring2025

## Spring 2025 Research Projects

This repository contains two related projects developed in Spring 2025 focused on evaluating and generating image captions using large vision-language models.

---

## 📁 Projects

### 1. `captionResearchProject/`

A research-driven pipeline for evaluating AI-generated image captions.  
It includes tools to:

- Generate image captions using local or remote models (e.g., Gemma, Kosmos-2)
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

## 🧪 Status

Both tools are functional and were used in real evaluation pipelines.  
You may need to adjust image paths, model names, or mounts depending on your system setup.
