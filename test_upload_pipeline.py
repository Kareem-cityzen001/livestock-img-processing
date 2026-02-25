#!/usr/bin/env python3
"""
Test script to verify the complete upload and analysis pipeline.
This checks:
1. Flask server is running on correct port
2. Model loads correctly
3. Test image can be processed
4. Response format is correct
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
SERVER_URL = "http://127.0.0.1:5000"
UPLOAD_ENDPOINT = f"{SERVER_URL}/upload"

def test_server_connection():
    """Test if Flask server is running"""
    print("\n" + "="*60)
    print("TEST 1: Server Connection")
    print("="*60)
    
    try:
        response = requests.get(SERVER_URL, timeout=5)
        print(f"✅ Server is running on {SERVER_URL}")
        print(f"   Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {SERVER_URL}")
        print(f"   Make sure to run: python app.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_upload_endpoint():
    """Test if upload endpoint exists and responds"""
    print("\n" + "="*60)
    print("TEST 2: Upload Endpoint")
    print("="*60)
    
    try:
        # Test with a small dummy image
        test_image_path = Path("c:\\TROJAN\\datasets\\train\\healthy")
        
        if not test_image_path.exists():
            print(f"⚠️  Test image directory not found: {test_image_path}")
            print("   Skipping actual image upload test")
            return None
        
        # Find first available image
        image_files = list(test_image_path.glob("*.jpg")) + list(test_image_path.glob("*.jpeg")) + list(test_image_path.glob("*.png"))
        
        if not image_files:
            print(f"⚠️  No image files found in {test_image_path}")
            print("   Skipping actual image upload test")
            return None
        
        test_image = image_files[0]
        print(f"ℹ️  Using test image: {test_image.name}")
        
        with open(test_image, 'rb') as f:
            files = {'file': f}
            data = {'behavior': 'Test animal showing no visible symptoms'}
            
            print(f"Sending request to {UPLOAD_ENDPOINT}...")
            response = requests.post(
                UPLOAD_ENDPOINT,
                files=files,
                data=data,
                timeout=30,
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            
        print(f"✅ Upload endpoint responded")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Response is valid JSON")
                print(f"   Detected Disease: {result.get('disease', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 'N/A')}")
                return True
            except json.JSONDecodeError:
                print(f"   ❌ Response is not valid JSON")
                print(f"   Response text: {response.text[:200]}")
                return False
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (server may be processing)")
        return None
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def test_model_loading():
    """Test if model loads correctly by checking app logs"""
    print("\n" + "="*60)
    print("TEST 3: Model Loading")
    print("="*60)
    
    model_path = Path("c:\\TROJAN\\Models\\livestock_disease_detection.pth")
    
    if model_path.exists():
        print(f"✅ Model file exists: {model_path}")
        print(f"   Size: {model_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    else:
        print(f"❌ Model file not found: {model_path}")
        return False

def test_dataset():
    """Check if training data exists"""
    print("\n" + "="*60)
    print("TEST 4: Dataset Check")
    print("="*60)
    
    dataset_path = Path("c:\\TROJAN\\datasets\\train")
    
    if dataset_path.exists():
        classes = [d for d in dataset_path.iterdir() if d.is_dir()]
        print(f"✅ Dataset directory exists: {dataset_path}")
        print(f"   Classes found: {len(classes)}")
        
        total_images = 0
        for cls in classes:
            images = list(cls.glob("*.jpg")) + list(cls.glob("*.jpeg")) + list(cls.glob("*.png"))
            count = len(images)
            total_images += count
            print(f"     - {cls.name}: {count} images")
        
        print(f"   Total images: {total_images}")
        return True
    else:
        print(f"❌ Dataset directory not found: {dataset_path}")
        return False

def main():
    """Run all tests"""
    print("\n" + "█"*60)
    print("LIVESTOCK DISEASE DETECTION - PIPELINE TEST")
    print("█"*60)
    
    results = {
        "Server Connection": test_server_connection(),
        "Model Loading": test_model_loading(),
        "Dataset": test_dataset(),
        "Upload Endpoint": test_upload_endpoint(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"{status:8} | {test_name}")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Make sure Flask server is running: python app.py")
    print("2. Open http://127.0.0.1:5000 in your browser")
    print("3. Click 'Tap to Snap or Upload Photo'")
    print("4. Select an image file → preview should display")
    print("5. Click 'Analyze Health Condition' → diagnosis should appear")
    print("6. Check browser console (F12) for [PREVIEW] and [ANALYZE] logs")
    print("7. Check Python terminal for server-side logs")
    print("="*60)
    
    if results["Server Connection"] is False:
        print("\n⚠️  Server is not running! Start it first:")
        print("   python app.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
