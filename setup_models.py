"""
Practical script to download and test pre-trained livestock disease detection models.
Supports multiple sources: Roboflow, Hugging Face, PyTorch Hub.
"""

import os
import json
import urllib.request
import torch
from pathlib import Path

def ensure_models_dir():
    """Create Models directory if it doesn't exist."""
    os.makedirs("Models", exist_ok=True)
    print("✓ Models directory ready")

def download_file(url, filename, chunk_size=8192):
    """Download a file with progress tracking."""
    print(f"\n⬇️  Downloading: {filename}")
    try:
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filename, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"  Progress: {downloaded/1024/1024:.1f}MB / {total_size/1024/1024:.1f}MB ({percent:.1f}%)", end='\r')
        
        print(f"\n✓ Downloaded: {filename} ({os.path.getsize(filename)/1024/1024:.1f}MB)")
        return True
    except Exception as e:
        print(f"\n✗ Error downloading: {e}")
        return False

def setup_roboflow_model():
    """
    Set up Roboflow model.
    https://universe.roboflow.com/
    """
    print("\n" + "="*70)
    print("ROBOFLOW MODEL SETUP")
    print("="*70)
    print("""
Steps to get a Roboflow model:
1. Go to https://universe.roboflow.com/
2. Search for: "livestock disease detection" or "cattle disease"
3. Click on a project
4. Download → PyTorch format
5. Extract the .pt file to Models/ folder

Example project: Cattle Disease Detection
You can then rename it to: livestock_disease_detection.pth

Command to install Roboflow SDK:
  pip install roboflow

Example code:
  from roboflow import Roboflow
  rf = Roboflow(api_key="YOUR_API_KEY")
  project = rf.workspace().project("livestock-disease-detection")
  dataset = project.version(1).download("pytorch")
""")

def setup_huggingface_model():
    """
    Set up Hugging Face model.
    """
    print("\n" + "="*70)
    print("HUGGING FACE MODEL SETUP")
    print("="*70)
    print("""
Steps to download from Hugging Face:
1. Visit: https://huggingface.co/models?task=image-classification
2. Filter by: livestock, cattle, disease detection
3. Use the code below:

pip install huggingface-hub

Example code:
""")
    
    hf_code = '''
from huggingface_hub import hf_hub_download

# Option 1: Download a specific model
model_path = hf_hub_download(
    repo_id="facebook/dino-vitb16",
    filename="pytorch_model.bin",
    cache_dir="./Models"
)
print(f"Model saved to: {model_path}")

# Option 2: Using transformers library
from transformers import pipeline

# Image classification pipeline
classifier = pipeline(
    "image-classification",
    model="google/vit-base-patch16-224"
)

# Your livestock disease image
result = classifier("path/to/livestock/image.jpg")
print(result)
'''
    print(hf_code)

def setup_pytorch_hub_model():
    """
    Set up PyTorch Hub model.
    """
    print("\n" + "="*70)
    print("PYTORCH HUB MODEL SETUP")
    print("="*70)
    print("""
Example code to download from PyTorch Hub:
""")
    
    pt_code = '''
import torch

# Load ResNet50 from PyTorch Hub
model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)

# Save the model
torch.save(model.state_dict(), 'Models/resnet50_pretrained.pth')
print("✓ Model saved!")

# Other available models:
# - alexnet
# - resnet18, resnet34, resnet50, resnet101, resnet152
# - vgg16, vgg19
# - squeezenet1_0, squeezenet1_1
# - densenet121, densenet169, densenet201, densenet161
# - inception_v3
# - googlenet
# - shufflenet_v2_x1_0
# - mnasnet1_0
# - mobilenet_v2, mobilenet_v3_small, mobilenet_v3_large
# - resnext50_32x4d, resnext101_32x8d
# - wide_resnet50_2, wide_resnet101_2
# - efficientnet_b0 through b7
'''
    print(pt_code)

def setup_custom_model():
    """
    Guide for training a custom model.
    """
    print("\n" + "="*70)
    print("TRAIN YOUR OWN MODEL")
    print("="*70)
    print("""
If you have a livestock disease dataset:

1. Organize your images:
   datasets/
   ├── train/
   │   ├── Healthy/
   │   │   ├── image1.jpg
   │   │   ├── image2.jpg
   │   │   └── ...
   │   ├── Mastitis/
   │   │   └── ...
   │   └── Lumpy_Skin_Disease/
   │       └── ...
   └── val/
       ├── Healthy/
       ├── Mastitis/
       └── Lumpy_Skin_Disease/

2. Run training:
   python train_model.py

3. Model will be saved to:
   Models/livestock_disease_detection.pth

The training script will:
✓ Download ResNet50 (ImageNet pre-trained)
✓ Fine-tune on your disease dataset
✓ Apply augmentation
✓ Save best model
✓ Display accuracy metrics
""")

def test_model_loading():
    """
    Test if models can be loaded properly.
    """
    print("\n" + "="*70)
    print("TEST MODEL LOADING")
    print("="*70)
    
    test_code = '''
import torch
from processing.disease_detection import load_model
from processing.image_preprocessing import preprocess_image

# Test 1: Load default model (ImageNet weights)
print("Test 1: Loading default model...")
model = load_model(num_classes=3, model_name="resnet50")
print("✓ Model loaded successfully")

# Test 2: Load custom weights
print("\\nTest 2: Loading custom weights...")
model = load_model(
    num_classes=3,
    weights_path="Models/livestock_disease_detection.pth",
    model_name="resnet50"
)
print("✓ Model with custom weights loaded")

# Test 3: Perform inference
print("\\nTest 3: Running inference...")
class_names = ["Healthy", "Mastitis", "Lumpy Skin Disease"]
image_tensor = preprocess_image("path/to/your/image.jpg")
result = detect_disease(image_tensor, model, class_names)
print("Diagnosis:", result["Diagnosis"])
print("Confidence:", result["Confidence"])
print("✓ Inference complete")
'''
    print("\nCreate a test_model.py file with:")
    print(test_code)
    print("\nThen run:")
    print("  python test_model.py")

def list_available_weights():
    """
    List available model weights.
    """
    print("\n" + "="*70)
    print("AVAILABLE MODEL WEIGHTS")
    print("="*70)
    
    ensure_models_dir()
    
    models_path = Path("Models")
    weights = list(models_path.glob("*.pth"))
    
    if weights:
        print(f"Found {len(weights)} model weight(s):")
        for w in weights:
            size = w.stat().st_size / (1024**2)
            print(f"  • {w.name} ({size:.1f}MB)")
    else:
        print("✗ No model weights found in Models/")
        print("\nTo add weights:")
        print("  1. Download from Roboflow/Hugging Face/PyTorch Hub")
        print("  2. Save to Models/ folder")
        print("  3. Update weights_path in app.py")

def main():
    """
    Main menu.
    """
    print("\n" + "="*70)
    print("LIVESTOCK DISEASE DETECTION - MODEL SETUP")
    print("="*70)
    print("""
Choose an option:
  1. Set up Roboflow model (RECOMMENDED)
  2. Set up Hugging Face model
  3. Set up PyTorch Hub model
  4. Train your own model
  5. Test model loading
  6. List available weights
  7. Exit
""")
    
    while True:
        choice = input("Enter option (1-7): ").strip()
        
        if choice == "1":
            setup_roboflow_model()
        elif choice == "2":
            setup_huggingface_model()
        elif choice == "3":
            setup_pytorch_hub_model()
        elif choice == "4":
            setup_custom_model()
        elif choice == "5":
            test_model_loading()
        elif choice == "6":
            list_available_weights()
        elif choice == "7":
            print("\n✓ Goodbye!")
            break
        else:
            print("✗ Invalid option. Please try again.")
        
        print("\n" + "-"*70)

if __name__ == "__main__":
    ensure_models_dir()
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║       LIVESTOCK DISEASE DETECTION - MODEL DOWNLOADER             ║
║                                                                   ║
║  Your project is already configured with ResNet50.               ║
║  For best results, add a pre-trained livestock disease model.    ║
║                                                                   ║
║  This tool will help you download and set up models.             ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Exited")
    except Exception as e:
        print(f"\n✗ Error: {e}")
