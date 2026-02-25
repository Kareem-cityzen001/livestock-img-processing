#!/usr/bin/env python3
"""
Comprehensive upload debugging script
Tests the complete pipeline step by step
"""
import os
import sys
from pathlib import Path

# Test imports
print("\n" + "="*70)
print("STEP 1: Testing Python Imports")
print("="*70)

required_modules = {
    'flask': 'Flask',
    'torch': 'PyTorch',
    'torchvision': 'TorchVision',
    'PIL': 'Pillow',
    'numpy': 'NumPy',
}

missing = []
for module, name in required_modules.items():
    try:
        __import__(module)
        print(f"✅ {name}")
    except ImportError as e:
        print(f"❌ {name}: {e}")
        missing.append(module)

if missing:
    print(f"\n⚠️  Missing modules: {', '.join(missing)}")
    print("Run: pip install " + " ".join(missing))

# Test image preprocessing
print("\n" + "="*70)
print("STEP 2: Testing Image Preprocessing")
print("="*70)

try:
    from processing.image_preprocessing import preprocess_image
    print("✅ Image preprocessing imported")
    
    # Find a test image
    test_image = None
    for path in Path("datasets/train").glob("*/*.jpg"):
        test_image = path
        break
    
    if test_image:
        print(f"\n   Test image: {test_image}")
        print(f"   Size: {test_image.stat().st_size / 1024:.1f} KB")
        
        # Try preprocessing
        result = preprocess_image(str(test_image))
        if result is not None:
            print(f"✅ Image preprocessing works")
            print(f"   Output shape: {result.shape}")
        else:
            print(f"❌ Image preprocessing returned None")
    else:
        print("⚠️  No test image found")
        
except Exception as e:
    print(f"❌ Image preprocessing error: {e}")
    import traceback
    traceback.print_exc()

# Test model loading
print("\n" + "="*70)
print("STEP 3: Testing Model Loading")
print("="*70)

try:
    from processing.disease_detection import load_model, detect_disease
    print("✅ Disease detection module imported")
    
    model = load_model(num_classes=3, weights_path="Models/livestock_disease_detection.pth")
    print("✅ Model loaded successfully")
    
    class_names = ['foot-and-mouth', 'healthy', 'lumpy']
    print(f"✅ Class names: {class_names}")
    
except Exception as e:
    print(f"❌ Model loading error: {e}")
    import traceback
    traceback.print_exc()

# Test complete pipeline
print("\n" + "="*70)
print("STEP 4: Testing Complete Pipeline")
print("="*70)

try:
    from processing.image_preprocessing import preprocess_image
    from processing.disease_detection import load_model, detect_disease
    import torch
    
    # Load model
    model = load_model(num_classes=3, weights_path="Models/livestock_disease_detection.pth")
    model.eval()
    print("✅ Model in eval mode")
    
    # Find test image
    test_image = None
    for path in Path("datasets/train").glob("*/*.jpg"):
        test_image = path
        break
    
    if test_image:
        # Preprocess
        processed = preprocess_image(str(test_image))
        print(f"✅ Image preprocessed: {processed.shape}")
        
        # Detect
        with torch.no_grad():
            class_names = ['foot-and-mouth', 'healthy', 'lumpy']
            result = detect_disease(processed, model, class_names)
            
        print(f"✅ Disease detection works")
        print(f"   Diagnosis: {result.get('Diagnosis', 'N/A')}")
        print(f"   Confidence: {result.get('Confidence', 'N/A')}")
        
except Exception as e:
    print(f"❌ Pipeline error: {e}")
    import traceback
    traceback.print_exc()

# Test Flask app
print("\n" + "="*70)
print("STEP 5: Testing Flask App")
print("="*70)

try:
    import app as flask_app
    print("✅ Flask app imports successfully")
    print(f"   Upload folder: {flask_app.app.config['UPLOAD_FOLDER']}")
    print(f"   Number of routes: {len(flask_app.app.url_map._rules)}")
    
    # List routes
    routes = [rule.rule for rule in flask_app.app.url_map.iter_rules()]
    print(f"   Routes: {', '.join(routes)}")
    
    if '/upload' in routes:
        print(f"✅ /upload route exists")
    else:
        print(f"❌ /upload route missing!")
        
except Exception as e:
    print(f"❌ Flask app error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
If all steps passed:
1. Start server: python app.py
2. Open: http://127.0.0.1:5000
3. Test upload in browser
4. Check browser console (F12) for [UPLOAD] errors
5. Check Python terminal for [DEBUG] messages

If any step failed:
- Install missing packages: pip install [module]
- Check dataset path: datasets/train/
- Verify model: Models/livestock_disease_detection.pth
- Review error logs above
""")
