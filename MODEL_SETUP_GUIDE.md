# Livestock Disease Detection - Pre-trained Model Setup Guide

## Overview

This project uses pre-trained deep learning models to detect livestock diseases from images. This guide explains how to obtain and use pre-trained models.

---

## ✅ Quick Start (Already Configured)

Your project is already set up to use **ResNet50** with ImageNet pre-trained weights. This provides a good baseline for transfer learning.

```python
# Your app.py already has this:
model = load_model(
    num_classes=len(class_names),
    weights_path="Models/livestock_disease_detection.pth",
    model_name="resnet50"
)
```

**To use immediately:** Just start the Flask app. The model will use ImageNet weights.

---

## 🎯 Getting Pre-trained Livestock Disease Models

### Option 1: **Roboflow (RECOMMENDED)** ⭐⭐⭐

Roboflow provides pre-trained models and datasets specifically for animal disease detection.

**Steps:**
1. Visit: https://universe.roboflow.com/
2. Search for: "cattle disease" or "livestock disease detection"
3. Download the dataset in **PyTorch** format
4. Extract weights to `Models/` folder
5. Update `app.py` with the correct path and class names

**Popular Roboflow Datasets:**
- Cattle Disease Detection
- Mastitis Classification
- Lumpy Skin Disease Detection

---

### Option 2: **Hugging Face Model Hub**

Download pre-trained models from the Hugging Face community:

```python
from huggingface_hub import hf_hub_download
import torch

# Install first: pip install huggingface-hub

# Download a livestock disease model
try:
    model_path = hf_hub_download(
        repo_id="huggingface/model-name",  # Replace with actual repo
        filename="pytorch_model.bin",
        cache_dir="./Models"
    )
    print(f"✓ Downloaded: {model_path}")
except Exception as e:
    print(f"Error: {e}")
```

**Search for:** https://huggingface.co/models?task=image-classification

---

### Option 3: **Train Your Own Model**

If you have a dataset of livestock disease images:

```bash
# 1. Organize your dataset:
datasets/
├── train/
│   ├── Healthy/
│   ├── Mastitis/
│   └── Lumpy_Skin_Disease/
└── val/
    ├── Healthy/
    ├── Mastitis/
    └── Lumpy_Skin_Disease/

# 2. Run training script:
python train_model.py
```

The script will:
- Download ResNet50 (ImageNet-pretrained)
- Fine-tune on your disease dataset
- Save weights to `Models/livestock_disease_detection.pth`

---

### Option 4: **GitHub Research Repositories**

Search GitHub for "livestock disease detection" or "cattle disease CNN":

Popular searches:
- `cattle disease deep learning`
- `mastitis detection model`
- `lumpy skin disease detection`

Clone repo and extract weights to `Models/` folder.

---

### Option 5: **Agricultural Research Datasets**

Free datasets to train your own model:

| Dataset | Link | Description |
|---------|------|-------------|
| **PlantVillage (Adaptable)** | https://github.com/spMohanty/PlantVillageDataset | Plant disease, can adapt methods |
| **Roboflow Open Source** | https://universe.roboflow.com/ | Various animal datasets |
| **Kaggle** | https://www.kaggle.com/datasets?search=cattle | Multiple livestock datasets |
| **ImageNet** | https://www.image-net.org/ | Large-scale image database |

---

## 📁 Project Structure Required

```
TROJAN/
├── app.py                          (Flask server)
├── train_model.py                  (Training script)
├── download_models.py              (Model setup guide)
├── Models/                         
│   └── livestock_disease_detection.pth  (Pre-trained weights)
├── processing/
│   ├── disease_detection.py        (Updated with new model loading)
│   └── image_preprocessing.py
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/script.js
└── uploads/                        (User uploaded images)
```

---

## 🔧 Available Model Architectures

Update `app.py` to choose different architectures:

```python
# Fastest (less accurate)
model = load_model(num_classes=3, model_name="resnet18")

# Balanced (DEFAULT)
model = load_model(num_classes=3, model_name="resnet50")

# Better accuracy (slower)
model = load_model(num_classes=3, model_name="efficientnet_b0")

# Best accuracy (slowest)
model = load_model(num_classes=3, model_name="efficientnet_b4")
```

---

## 📦 Installation

```bash
# Install required packages
pip install flask flask-cors torch torchvision pillow

# Optional (for Hugging Face models)
pip install huggingface-hub

# Optional (for Roboflow datasets)
pip install roboflow
```

---

## ⚙️ Configuration in `app.py`

```python
# Define your disease classes
class_names = ["Healthy", "Mastitis", "Lumpy Skin Disease"]

# Load model with custom weights
model = load_model(
    num_classes=len(class_names),
    weights_path="Models/livestock_disease_detection.pth",
    model_name="resnet50"  # or resnet18, efficientnet_b0, efficientnet_b4
)
```

**The model will:**
1. Look for weights at `Models/livestock_disease_detection.pth`
2. If not found, use ImageNet pre-trained weights
3. Adjust final layer for your number of classes

---

## 🚀 Running Your Application

```bash
# 1. Prepare Models directory
python download_models.py

# 2. (Optional) Train on your dataset
python train_model.py

# 3. Start Flask server
python app.py
```

Then visit: `http://localhost:5000`

---

## 📊 Understanding Model Outputs

The API returns:

```json
{
  "Diagnosis": "Mastitis",
  "Confidence": "94.23%",
  "All_Predictions": {
    "Healthy": "2.34%",
    "Mastitis": "94.23%",
    "Lumpy Skin Disease": "3.43%"
  },
  "Recommendation": "Mastitis detected. Recommend veterinary consultation and treatment."
}
```

---

## 🔍 Validation & Testing

```python
# Test the model with a sample image
from processing.image_preprocessing import preprocess_image
from processing.disease_detection import detect_disease

image_tensor = preprocess_image("path/to/image.jpg")
result = detect_disease(image_tensor, model, class_names)
print(result)
```

---

## ⚠️ Important Notes

1. **ImageNet Pre-trained Weights:** The model uses weights pre-trained on ImageNet. This provides good transfer learning for disease detection.

2. **Fine-tuning Recommended:** For best accuracy, fine-tune the model on your specific livestock disease dataset using `train_model.py`.

3. **GPU Acceleration:** Training is much faster with GPU. Uses CPU as fallback.

4. **Class Names Order:** Must match the order of your training data folder names.

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Error: "Models directory not found" | Run `python download_models.py` |
| Error: "weights not found" | Model will use ImageNet weights (fallback). Add custom weights to `Models/` |
| Low accuracy | Fine-tune the model using `train_model.py` on your disease dataset |
| GPU not detected | Model automatically falls back to CPU |
| Slow inference | Use `resnet18` or `efficientnet_b0` for faster models |

---

## 📚 References & Resources

- **PyTorch Models:** https://pytorch.org/vision/stable/models.html
- **Transfer Learning Guide:** https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
- **Roboflow:** https://roboflow.com/
- **Hugging Face:** https://huggingface.co/models
- **Kaggle Livestock Datasets:** https://www.kaggle.com/search?q=livestock

---

## 💡 Next Steps

1. ✅ Project is ready to use with ImageNet pre-trained weights
2. 🔄 Option A: Download pre-trained disease detection model from Roboflow
3. 🔄 Option B: Train your own model with `train_model.py`
4. 📤 Upload and test with livestock disease images

---

**Happy livestock disease detection! 🐄🐑🐖**
