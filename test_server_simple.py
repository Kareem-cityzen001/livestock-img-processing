#!/usr/bin/env python3
"""
Minimal upload test - just check if the upload endpoint works
"""
import os
import sys

# Quick import check
print("Importing Flask...")
try:
    from flask import Flask, request, jsonify
    print("✅ Flask OK")
except Exception as e:
    print(f"❌ Flask failed: {e}")
    sys.exit(1)

print("Importing PyTorch...")
try:
    import torch
    print("✅ PyTorch OK")
except Exception as e:
    print(f"❌ PyTorch failed: {e}")
    sys.exit(1)

print("Importing image processing...")
try:
    from processing.image_preprocessing import preprocess_image
    print("✅ Image preprocessing OK")
except Exception as e:
    print(f"❌ Image preprocessing failed: {e}")
    sys.exit(1)

print("Importing disease detection...")
try:
    from processing.disease_detection import load_model, detect_disease
    print("✅ Disease detection OK")
except Exception as e:
    print(f"❌ Disease detection failed: {e}")
    sys.exit(1)

print("\n✅ All imports successful!")
print("\nStarting Flask server on http://127.0.0.1:5000")
print("Press Ctrl+C to stop\n")

# Quick app
app = Flask(__name__)

@app.route("/")
def index():
    return "Server is running!"

@app.route("/test-upload", methods=["POST"])
def test_upload():
    print("\n[TEST] Upload request received!")
    if "image" not in request.files:
        return jsonify({"error": "No image"}), 400
    
    file = request.files["image"]
    print(f"[TEST] Got file: {file.filename}")
    return jsonify({"status": "ok", "filename": file.filename})

if __name__ == "__main__":
    try:
        app.run(debug=False, port=5000, host='127.0.0.1')
    except KeyboardInterrupt:
        print("\nServer stopped")
