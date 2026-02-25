"""
Test the livestock disease detection model with sample images
"""

import torch
import os
from PIL import Image
from processing.disease_detection import detect_disease, load_model
from processing.image_preprocessing import preprocess_image

def test_model_inference():
    """Test model with sample image."""
    
    print("\n" + "="*70)
    print("LIVESTOCK DISEASE DETECTION - MODEL TEST")
    print("="*70)
    
    # Define diseases
    class_names = [
        "Healthy",
        "Lumpy Skin Disease",
        "Foot Rot",
        "Mastitis",
        "Blackleg",
        "Anthrax Disease",
        "Tick-Borne Fever"
    ]
    
    print(f"\n✓ Loading model...")
    try:
        model = load_model(
            num_classes=len(class_names),
            weights_path="Models/livestock_disease_detection.pth",
            model_name="resnet50"
        )
        print(f"✓ Model loaded successfully!")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return
    
    print(f"✓ Model classes: {len(class_names)}")
    for i, disease in enumerate(class_names, 1):
        print(f"   {i}. {disease}")
    
    # Check for test images
    print(f"\n" + "-"*70)
    print("TESTING WITH IMAGES")
    print("-"*70)
    
    test_images = []
    
    # Check uploads folder
    if os.path.exists("uploads"):
        for file in os.listdir("uploads"):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                test_images.append(os.path.join("uploads", file))
    
    # Check static folder
    if os.path.exists("static"):
        for root, dirs, files in os.walk("static"):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    test_images.append(os.path.join(root, file))
    
    if not test_images:
        print("""
✗ No test images found!

To test the model with images:
1. Place livestock images in the 'uploads/' folder
2. Supported formats: .jpg, .jpeg, .png, .bmp
3. Run this script again

To use via web interface:
1. Run: python app.py
2. Open: http://localhost:5000
3. Upload livestock image
4. Get instant diagnosis!
""")
        return
    
    print(f"\nFound {len(test_images)} test image(s):\n")
    
    # Test each image
    for image_path in test_images[:5]:  # Test first 5 images
        print(f"Testing: {image_path}")
        print("-" * 70)
        
        try:
            # Preprocess image
            image_tensor = preprocess_image(image_path)
            
            # Detect disease
            result = detect_disease(image_tensor, model, class_names)
            
            # Display results
            print(f"  Diagnosis:  {result['Diagnosis']}")
            print(f"  Confidence: {result['Confidence']}")
            print(f"  Status:     {result['Status']}")
            print(f"  Severity:   {result['Severity']}")
            print(f"  Action:     {result['Action']}")
            print(f"  Treatment:  {result['Treatment']}")
            print(f"  Contagious: {result['Contagious']}")
            print(f"  Quarantine: {result['Quarantine']}")
            
            # Show all predictions
            print(f"\n  All Predictions:")
            for disease, prob in sorted(result['All_Predictions'].items(), 
                                       key=lambda x: float(x[1].rstrip('%')), 
                                       reverse=True):
                print(f"    • {disease}: {prob}")
            
            print()
        
        except Exception as e:
            print(f"  ✗ Error: {e}\n")

def create_test_image():
    """Create a simple test image for demonstration."""
    try:
        from PIL import Image, ImageDraw
        import random
        
        os.makedirs("uploads", exist_ok=True)
        
        # Create a test image (224x224 with some color)
        size = 224
        img = Image.new('RGB', (size, size), color=(random.randint(50, 200), 
                                                      random.randint(50, 200), 
                                                      random.randint(50, 200)))
        
        # Add some shapes to make it look like an animal
        draw = ImageDraw.Draw(img)
        draw.ellipse([50, 50, 174, 174], fill=(random.randint(100, 220), 
                                               random.randint(100, 220), 
                                               random.randint(100, 220)))
        
        test_image_path = "uploads/test_image.jpg"
        img.save(test_image_path)
        print(f"✓ Created test image: {test_image_path}")
        
        return test_image_path
    except Exception as e:
        print(f"Could not create test image: {e}")
        return None

def show_model_info():
    """Display model information."""
    print("\n" + "="*70)
    print("MODEL INFORMATION")
    print("="*70)
    
    if os.path.exists("Models/livestock_disease_detection.pth"):
        size = os.path.getsize("Models/livestock_disease_detection.pth")
        print(f"\n✓ Model file exists")
        print(f"  Location: Models/livestock_disease_detection.pth")
        print(f"  Size: {size / (1024**2):.1f} MB")
        print(f"  Architecture: ResNet50")
        print(f"  Pre-trained on: ImageNet")
        print(f"  Classes: 7 livestock diseases")
        print(f"  Input size: 224×224 pixels")
        print(f"  Output: Disease classification + confidence")
    else:
        print("\n✗ Model file not found!")
        print("  Run: python create_pretrained_model.py")

if __name__ == "__main__":
    try:
        # Show model info
        show_model_info()
        
        # Create test image if none exist
        test_dir = "uploads"
        if not os.path.exists(test_dir) or not any(f.endswith(('.jpg', '.png', '.bmp')) for f in os.listdir(test_dir)):
            print("\nNo test images found. Creating sample test image...")
            create_test_image()
        
        # Test model
        test_model_inference()
        
        print("\n" + "="*70)
        print("✓ Test complete!")
        print("="*70)
        print("""
Next steps:
1. Upload your own livestock images to the 'uploads/' folder
2. Run this test again to see predictions
3. Or use the web interface: python app.py
""")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
