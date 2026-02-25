#!/usr/bin/env python3
"""
Direct test of upload endpoint to diagnose issues
"""
import requests
import sys
from pathlib import Path

print("\n" + "="*70)
print("UPLOAD ENDPOINT TEST")
print("="*70)

SERVER_URL = "http://127.0.0.1:5000"
UPLOAD_URL = f"{SERVER_URL}/upload"

# Find a test image
test_image_path = None
for path in [
    Path("datasets/train/healthy"),
    Path("datasets/train/foot-and-mouth"),
    Path("datasets/train/lumpy"),
    Path("uploads")
]:
    if path.exists():
        images = list(path.glob("*.jpg")) + list(path.glob("*.jpeg")) + list(path.glob("*.png"))
        if images:
            test_image_path = images[0]
            break

if not test_image_path:
    print("\n❌ No test image found in:")
    print("   - datasets/train/healthy/")
    print("   - datasets/train/foot-and-mouth/")
    print("   - datasets/train/lumpy/")
    sys.exit(1)

print(f"\n✅ Using test image: {test_image_path}")
print(f"   Size: {test_image_path.stat().st_size / 1024:.1f} KB")

# Test 1: Check server responds
print("\n" + "-"*70)
print("TEST 1: Server Connection")
print("-"*70)
try:
    response = requests.get(f"{SERVER_URL}/", timeout=5)
    print(f"✅ Server is running (status: {response.status_code})")
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")
    sys.exit(1)

# Test 2: Upload test image
print("\n" + "-"*70)
print("TEST 2: Upload Image")
print("-"*70)
try:
    with open(test_image_path, 'rb') as f:
        files = {'image': f}
        data = {'behavior_description': 'Test animal with no visible symptoms'}
        
        print(f"Uploading to: {UPLOAD_URL}")
        print(f"Files: {files.keys()}")
        print(f"Data: {data.keys()}")
        
        response = requests.post(
            UPLOAD_URL,
            files=files,
            data=data,
            timeout=30,
            headers={'User-Agent': 'TestClient/1.0'}
        )
        
        print(f"\n✅ Response received")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\n✅ UPLOAD SUCCESSFUL!")
                print(f"\nDigosis Result:")
                print(f"   Diagnosis: {result.get('Diagnosis', 'N/A')}")
                print(f"   Confidence: {result.get('Confidence', 'N/A')}")
                print(f"   Status: {result.get('Status', 'N/A')}")
                print(f"   Action: {result.get('Action', 'N/A')}")
            except:
                print(f"\n⚠️  Response is not JSON")
                print(f"Response content:\n{response.text[:500]}")
        else:
            print(f"\n❌ UPLOAD FAILED (Status: {response.status_code})")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Response:\n{response.text[:500]}")
                
except requests.exceptions.Timeout:
    print("❌ Request timed out (server may be slow)")
except Exception as e:
    print(f"❌ Error during upload: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
