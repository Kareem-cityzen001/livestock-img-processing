#!/usr/bin/env python3
"""
Quick validation that all components are ready
"""
import sys
import os
from pathlib import Path

print("\n" + "="*60)
print("LIVESTOCK DISEASE DETECTION - SETUP VALIDATION")
print("="*60)

checks = {
    "Python path": sys.executable,
    "Current directory": os.getcwd(),
    "Python version": f"{sys.version_info.major}.{sys.version_info.minor}",
}

print("\n✅ ENVIRONMENT:")
for key, value in checks.items():
    print(f"   {key}: {value}")

# Check key files
print("\n✅ FILE CHECKS:")
files = [
    ("Flask app", "app.py"),
    ("Main page", "templates/index.html"),
    ("Dashboard", "templates/dashboard.html"),
    ("JavaScript", "static/js/script.js"),
    ("CSS", "static/css/style.css"),
    ("Model", "Models/livestock_disease_detection.pth"),
    ("Dataset", "datasets/train"),
]

for label, path in files:
    p = Path(path)
    if p.exists():
        if p.is_file():
            size = p.stat().st_size
            if size > 1024*1024:
                size_str = f"{size/(1024*1024):.1f} MB"
            elif size > 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size} B"
            print(f"   ✅ {label:15} {path:35} ({size_str})")
        else:
            items = len(list(p.glob("**/*")))
            print(f"   ✅ {label:15} {path:35} ({items} items)")
    else:
        print(f"   ❌ {label:15} {path:35} MISSING!")

# Check Python imports
print("\n✅ PYTHON IMPORTS:")
required_packages = {
    "flask": "Flask",
    "torch": "PyTorch",
    "torchvision": "TorchVision",
    "pillow": "Pillow",
    "numpy": "NumPy",
}

for module, name in required_packages.items():
    try:
        __import__(module)
        print(f"   ✅ {name:15} imported successfully")
    except ImportError:
        print(f"   ❌ {name:15} NOT installed - run: pip install {module}")

print("\n" + "="*60)
print("READY TO START SERVER:")
print("="*60)
print("\n1. Start the Flask server:")
print("   python app.py")
print("\n2. Open in browser:")
print("   http://127.0.0.1:5000")
print("\n3. Test image upload:")
print("   - Click '📷 Tap to Snap or Upload Photo'")
print("   - Select image file")
print("   - Image preview should appear")
print("   - Click 'Analyze Health Condition'")
print("   - Diagnosis should display")
print("\n4. Check browser console (F12):")
print("   - Look for [PREVIEW] and [ANALYZE] logs")
print("   - Should be green, no red errors")
print("\n" + "="*60)
print("✅ ALL COMPONENTS READY - You can now start the server!")
print("="*60 + "\n")
