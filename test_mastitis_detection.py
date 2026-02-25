"""
Test Mastitis detection without the web interface.
Run this after training to test the model directly.
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import glob

class MastitisDetectionTester:
    """Test trained Mastitis detection model."""
    
    def __init__(self, model_path="Models/livestock_disease_detection.pth"):
        """Initialize tester."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.model = None
        self.class_names = None
        
        self.load_model()
    
    def load_model(self):
        """Load trained model."""
        if not os.path.exists(self.model_path):
            print(f"❌ Model not found: {self.model_path}")
            return False
        
        print(f"📦 Loading model from {self.model_path}...")
        
        try:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            # Extract info
            self.class_names = checkpoint.get('class_names', [])
            num_classes = checkpoint.get('num_classes', len(self.class_names))
            
            print(f"✓ Classes: {', '.join(self.class_names)}")
            print(f"✓ Accuracy from training: {checkpoint.get('accuracy', 'N/A')}%")
            
            # Build model
            self.model = models.resnet50()
            in_features = self.model.fc.in_features
            self.model.fc = nn.Linear(in_features, num_classes)
            
            # Load weights
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model = self.model.to(self.device)
            self.model.eval()
            
            print("✓ Model loaded successfully!\n")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def predict(self, image_path):
        """Predict disease from image."""
        
        try:
            # Load image
            img = Image.open(image_path).convert('RGB')
            
            # Transform
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            img_tensor = transform(img).unsqueeze(0).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(img_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            class_idx = predicted.item()
            class_name = self.class_names[class_idx]
            conf_score = confidence.item() * 100
            
            return {
                'disease': class_name,
                'confidence': conf_score,
                'all_scores': {
                    self.class_names[i]: probabilities[0][i].item() * 100 
                    for i in range(len(self.class_names))
                }
            }
            
        except Exception as e:
            print(f"❌ Error processing image: {e}")
            return None
    
    def test_directory(self, directory):
        """Test all images in a directory."""
        
        print(f"\n📁 Testing images in: {directory}")
        print("="*70)
        
        image_files = glob.glob(os.path.join(directory, "*.*"))
        image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not image_files:
            print(f"⚠️  No images found in {directory}")
            return
        
        print(f"Found {len(image_files)} images\n")
        
        for img_path in image_files:
            img_name = os.path.basename(img_path)
            result = self.predict(img_path)
            
            if result:
                print(f"📷 {img_name}")
                print(f"   → {result['disease']}: {result['confidence']:.1f}%")
                
                # Show all scores
                print(f"   All predictions:")
                for disease, score in sorted(result['all_scores'].items(), key=lambda x: x[1], reverse=True):
                    bar = "█" * int(score / 5)
                    print(f"      {disease:20s}: {score:5.1f}% {bar}")
                print()
    
    def test_mastitis_specific(self):
        """Test Mastitis detection if Mastitis directory exists."""
        
        mastitis_path = "datasets/train/Mastitis"
        
        if not os.path.exists(mastitis_path):
            print(f"⚠️  Mastitis test images not found at {mastitis_path}")
            return
        
        print(f"\n🔬 MASTITIS DETECTION TEST")
        print("="*70)
        
        self.test_directory(mastitis_path)
        
        # Summary
        print("="*70)
        if "Mastitis" in self.class_names:
            mastitis_idx = self.class_names.index("Mastitis")
            print(f"✅ Mastitis detection enabled (class index: {mastitis_idx})")
        else:
            print("⚠️  Mastitis class not found in model!")


def main():
    print("\n" + "="*70)
    print("🔬 MASTITIS MODEL TESTER")
    print("="*70 + "\n")
    
    print("This tool tests your trained Mastitis detection model.")
    print("Usage:\n")
    print("  1. Run this script after training completes")
    print("  2. It will test images from datasets/train/")
    print("  3. Shows confidence scores for each disease")
    
    # Initialize tester
    tester = MastitisDetectionTester()
    
    if tester.model is None:
        print("\n❌ Could not load model. Training may not be complete yet.")
        return
    
    # Test Mastitis images  
    tester.test_mastitis_specific()
    
    # Test other classes
    print("\n" + "="*70)
    print("📊 TESTING OTHER DISEASE CLASSES")
    print("="*70)
    
    for class_name in ['healthy', 'lumpy', 'foot-and-mouth']:
        test_dir = f"datasets/train/{class_name}"
        if os.path.exists(test_dir):
            images = glob.glob(os.path.join(test_dir, "*.*"))
            images = [f for f in images if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if images:
                # Test first image only for speed
                result = tester.predict(images[0])
                if result:
                    print(f"\n{class_name.upper()}:")
                    print(f"  First image predicted as: {result['disease']} ({result['confidence']:.1f}%)")
    
    print("\n" + "="*70)
    print("✅ Testing complete!")
    print("   If Mastitis detection confidence is good, your model is ready!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
