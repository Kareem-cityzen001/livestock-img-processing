"""
Script to download and set up pre-trained livestock disease detection models.
Supports multiple model sources and formats.
"""

import os
import json
import torch
from pathlib import Path

# Create Models directory
os.makedirs("Models", exist_ok=True)

print("=" * 70)
print("LIVESTOCK DISEASE DETECTION - MODEL SETUP GUIDE")
print("=" * 70)

print("""
OPTION 1: Use Roboflow Pre-trained Models (RECOMMENDED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Visit: https://universe.roboflow.com/?model=object-detection
Search for: "livestock disease detection" or "cattle disease"

Popular datasets:
• Cattle Disease Detection (Roboflow)
• Mastitis Detection Dataset
• Lumpy Skin Disease Dataset

Steps:
1. Go to Roboflow Universe
2. Download the dataset in PyTorch format
3. Extract to your project

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


OPTION 2: Use Hugging Face Model Hub
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Install: pip install huggingface_hub

Example model download:
""")

# Create sample model downloading function
sample_download_code = '''
from huggingface_hub import hf_hub_download

# Download a livestock disease detection model
try:
    model_path = hf_hub_download(
        repo_id="nateraw/animals",  # Example repo
        filename="model.pt",
        cache_dir="./Models"
    )
    print(f"✓ Downloaded model to: {model_path}")
except Exception as e:
    print(f"✗ Could not download: {e}")
'''

print(sample_download_code)

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


OPTION 3: Fine-tune on Your Own Dataset
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Create datasets/
├── train/
│   ├── Healthy/
│   ├── Mastitis/
│   └── Lumpy_Skin_Disease/
└── test/
    ├── Healthy/
    ├── Mastitis/
    └── Lumpy_Skin_Disease/

Then use: train_model.py (create this file)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


OPTION 4: Use Pre-trained Weights from Research
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Common sources:
• Papers with Code: https://paperswithcode.com/
• GitHub Research Repos
• AnimalAI Zoo: https://animalai.azurewebsites.net/

""")

print("\n" + "=" * 70)
print("QUICK START: Using Default (ImageNet-pretrained)")
print("=" * 70)
print("""
Your app.py is already configured to use ResNet50 with ImageNet 
pre-trained weights. This provides a good baseline for transfer learning.

The model will be loaded from:
  - Models/livestock_disease_detection.pth (if you add custom weights)
  - Or use ImageNet weights as fallback

To add custom weights:
1. Train on your livestock disease dataset OR
2. Download a pre-trained model from one of the options above
3. Save it as: Models/livestock_disease_detection.pth
4. Restart your Flask app

You can also specify different model architectures in app.py:
  - model_name="resnet18"        (faster, less accurate)
  - model_name="resnet50"        (balanced - default)
  - model_name="efficientnet_b0" (faster, good accuracy)
  - model_name="efficientnet_b4" (best accuracy, slower)
""")

# Check what we have
print("\n" + "=" * 70)
print("CURRENT STATUS")
print("=" * 70)

if os.path.exists("Models"):
    models_in_dir = os.listdir("Models")
    if models_in_dir:
        print(f"✓ Found {len(models_in_dir)} file(s) in Models/:")
        for f in models_in_dir:
            size = os.path.getsize(f"Models/{f}") / (1024**2)
            print(f"  • {f} ({size:.1f} MB)")
    else:
        print("✗ Models/ directory exists but is empty")
        print("  → Add .pth files here when you have trained models")
else:
    print("✓ Models directory created at: Models/")

print("\n" + "=" * 70)
