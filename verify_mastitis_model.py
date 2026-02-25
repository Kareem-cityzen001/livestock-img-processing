"""
Verify that the trained model includes Mastitis class.
Run this after training completes.
"""

import torch
import os

def verify_model():
    """Verify model and show class information."""
    
    model_path = "Models/livestock_disease_detection.pth"
    
    if not os.path.exists(model_path):
        print(f"\n❌ Model not found at: {model_path}")
        print("  Did training complete successfully?")
        return False
    
    print(f"\n{'='*70}")
    print("🔍 MODEL VERIFICATION")
    print(f"{'='*70}")
    
    try:
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location='cpu')
        
        print(f"\n✓ Model loaded successfully")
        
        # Extract info
        classes = checkpoint.get('class_names', [])
        num_classes = checkpoint.get('num_classes', len(classes))
        accuracy = checkpoint.get('accuracy', 'N/A')
        epoch = checkpoint.get('epoch', 'N/A')
        model_name = checkpoint.get('model_name', 'Unknown')
        
        print(f"\n📊 Model Information:")
        print(f"  • Architecture: {model_name}")
        print(f"  • Number of classes: {num_classes}")
        print(f"  • Training epoch: {epoch}")
        print(f"  • Validation accuracy: {accuracy}%")
        
        # Check for classes
        print(f"\n📋 Classes Detected:")
        if not classes:
            print("  ⚠️  No classes found in checkpoint!")
            return False
        
        for idx, cls in enumerate(classes):
            mastitis_indicator = " ← MASTITIS!" if "Mastitis" in cls else ""
            print(f"  [{idx}] {cls}{mastitis_indicator}")
        
        # Verify Mastitis
        has_mastitis = any("Mastitis" in cls for cls in classes)
        
        print(f"\n{'='*70}")
        if has_mastitis:
            print("✅ MASTITIS DETECTION ENABLED!")
            print("   Model is ready to detect Mastitis!")
        else:
            print("⚠️  WARNING: Mastitis not found in class list")
            print("   Check if Mastitis folder exists in datasets/train/")
        
        print(f"{'='*70}\n")
        
        return has_mastitis
        
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_dataset():
    """Check if Mastitis dataset exists."""
    
    import os
    
    print(f"\n{'='*70}")
    print("📁 DATASET CHECK")
    print(f"{'='*70}\n")
    
    base_path = "datasets/train"
    
    if not os.path.exists(base_path):
        print(f"❌ Dataset not found: {base_path}")
        return False
    
    classes = os.listdir(base_path)
    print(f"✓ Found {len(classes)} classes:")
    
    for cls in sorted(classes):
        path = os.path.join(base_path, cls)
        if os.path.isdir(path):
            num_images = len([f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
            indicator = " ← Training target!" if "Mastitis" in cls else ""
            print(f"  • {cls}: {num_images} images{indicator}")
    
    print(f"\n{'='*70}\n")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔬 MODEL AND DATASET VERIFICATION TOOL")
    print("="*70)
    
    # Check dataset
    check_dataset()
    
    # Verify model
    success = verify_model()
    
    if success:
        print("\n✅ Everything looks good!")
        print("   Your model is ready to detect Mastitis!")
        print("\n   Next steps:")
        print("   1. Restart your app.py")
        print("   2. Upload a cow image")
        print("   3. Add behavioral notes")
        print("   4. Get Mastitis detection!")
    else:
        print("\n⚠️  Model verification failed.")
        print("   Check the training output above.")
