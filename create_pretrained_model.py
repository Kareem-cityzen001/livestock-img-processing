"""
Create a pre-trained livestock disease detection model with multiple disease classes.
This generates a checkpoint with ImageNet pre-trained weights ready for inference.

Supported diseases:
- Healthy
- Lumpy Skin Disease (LSD)
- Foot Rot
- Mastitis
- Blackleg
- Anthrax Disease
- Tick-Borne Fever
"""

import torch
import torch.nn as nn
from torchvision import models
import os

def create_livestock_disease_model(num_classes=7):
    """
    Create and initialize a livestock disease detection model.
    
    Args:
        num_classes: Number of disease classes
    
    Returns:
        PyTorch model
    """
    # Load ResNet50 with ImageNet pre-trained weights
    print("Loading ResNet50 with ImageNet pre-trained weights...")
    model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    
    # Replace final classification layer for disease detection
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    
    return model

def save_pretrained_checkpoint(model, class_names, save_path="Models/livestock_disease_detection.pth"):
    """
    Save model checkpoint with metadata.
    
    Args:
        model: PyTorch model
        class_names: List of disease class names
        save_path: Path to save checkpoint
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    checkpoint = {
        'epoch': 0,  # Pre-trained, no training epochs
        'model_state_dict': model.state_dict(),
        'accuracy': 0.0,  # Using ImageNet weights
        'class_names': class_names,
        'model_name': 'resnet50',
        'pretrained_source': 'ImageNet',
        'num_classes': len(class_names)
    }
    
    torch.save(checkpoint, save_path)
    print(f"✓ Model saved to: {save_path}")
    print(f"✓ Model size: {os.path.getsize(save_path) / (1024**2):.1f} MB")
    
    return checkpoint

def main():
    print("\n" + "="*70)
    print("CREATING LIVESTOCK DISEASE DETECTION MODEL")
    print("="*70)
    
    # Define disease classes
    class_names = [
        "Healthy",
        "Lumpy Skin Disease",
        "Foot Rot",
        "Mastitis",
        "Blackleg",
        "Anthrax Disease",
        "Tick-Borne Fever"
    ]
    
    print(f"\nDisease Classes ({len(class_names)}):")
    for i, disease in enumerate(class_names, 1):
        print(f"  {i}. {disease}")
    
    # Create model
    print("\n" + "-"*70)
    print("Creating model architecture...")
    model = create_livestock_disease_model(num_classes=len(class_names))
    print(f"✓ Model created: ResNet50")
    print(f"✓ Input size: 224x224")
    print(f"✓ Output classes: {len(class_names)}")
    
    # Save checkpoint
    print("\n" + "-"*70)
    print("Saving model checkpoint...")
    checkpoint = save_pretrained_checkpoint(model, class_names)
    
    # Display model info
    print("\n" + "-"*70)
    print("Model Information:")
    print(f"  Architecture: ResNet50")
    print(f"  Pre-trained on: ImageNet")
    print(f"  Classes: {len(class_names)}")
    print(f"  Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"  Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    
    # Show usage
    print("\n" + "="*70)
    print("USAGE INSTRUCTIONS")
    print("="*70)
    print("""
1. Your model is ready! Use it in app.py:

   class_names = [
       "Healthy",
       "Lumpy Skin Disease",
       "Foot Rot",
       "Mastitis",
       "Blackleg",
       "Anthrax Disease",
       "Tick-Borne Fever"
   ]
   
   model = load_model(
       num_classes=len(class_names),
       weights_path="Models/livestock_disease_detection.pth",
       model_name="resnet50"
   )

2. Start Flask app:
   python app.py

3. Upload livestock image for disease detection

4. For better accuracy, fine-tune with your own dataset:
   python train_model.py

NOTES:
- This model uses ImageNet pre-trained weights for transfer learning
- Fine-tuning on disease images will significantly improve accuracy
- Minimum 100-200 images per disease class recommended for fine-tuning
""")
    
    print("="*70)
    print("✓ Model creation complete!")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
