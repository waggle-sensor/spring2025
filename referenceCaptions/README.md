# 📝 Ground Truth Captions for Image Captioning Evaluation

This folder contains manually written **reference captions** used for evaluating the performance of vision-language models on rural and urban datasets. Each JSON file adheres to a COCO-style format with detailed metadata, image descriptors, and corresponding captions. In the directory `modelCaptions/` you can find the caption outputs from models corresponding to these human captions.

---

## 📂 File Overview

Each JSON file corresponds to a specific **image batch** and a unique **set of human-written captions**:

| Filename                                   | Description                                  |
|--------------------------------------------|----------------------------------------------|
| `groundTruth_ruralBatch1_referencecaption1.json` | First reference caption set for Rural Batch 1 |
| `groundTruth_ruralBatch1_referencecaption2.json` | Second reference caption set for Rural Batch 1 |
| `groundTruth_ruralBatch2_referencecaption1.json` | First reference caption set for Rural Batch 2 |
| `groundTruth_ruralBatch2_referencecaption2.json` | Second reference caption set for Rural Batch 2 |
| `groundTruth_urbanBatch1_referencecaption1.json` | First reference caption set for Urban Batch 1 |
| `groundTruth_urbanBatch1_referencecaption2.json` | Second reference caption set for Urban Batch 1 |
| `groundTruth_urbanBatch2_referencecaption1.json` | First reference caption set for Urban Batch 2 |
| `groundTruth_urbanBatch2_referencecaption2.json` | Second reference caption set for Urban Batch 2 |
| `modelCaptions/` | Model caption outputs used in study |


Each file provides an independent reference that helps reduce evaluation bias in metrics like BLEU, METEOR, ROUGE, BERTScore, and CLIPScore.

---

## 🧾 JSON File Structure

Each file follows the [COCO-style annotation](https://cocodataset.org/#format-data) format with the following sections:

### `images` (list of image metadata)

Each entry includes:

```json
{
  "file_name": "20240508 034929_nan_W01E_sample.jpg",
  "date_time_taken": "2024-05-08T03:49:29.499Z",
  "node": "000048b02d15bc3d",
  "camera": "left_camera",
  "vsn": "W01E",
  "url": "https://storage.sagecontinuum.org/api/v1/data/...",
  "width": 2560,
  "height": 1920,
  "id": 1
}
```

### `annotations` (list of captions with labels)

Each caption is mapped to an image ID:

```json
{
  "id": 1,
  "image_id": 1,
  "caption": "A night scene of a chain link fence with a light illuminating foliage in front of it.",
  "labels": ["night", "chain", "fence", "light", "foliage"]
}
```

Note: Keyword extraction was originally part of the project scope but was ultimately excluded from the final implementation.
