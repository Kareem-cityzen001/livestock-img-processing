"""
Roboflow Dataset Download Script
Download a livestock disease classification dataset
"""

import os
import requests
from roboflow import Roboflow
import shutil

print("\n" + "="*70)
print("ROBOFLOW LIVESTOCK DISEASE DATASET DOWNLOADER")
print("="*70)

# Get API key from user
api_key = input("\nEnter your Roboflow Private API Key: ").strip()

if not api_key:
    print("❌ API key required!")
    exit(1)

try:
    print("\n🔄 Authenticating with Roboflow...")
    rf = Roboflow(api_key=api_key)
    
    # Try to get a livestock disease detection project
    # You can replace with your specific project name if you have one
    print("📊 Searching for livestock disease datasets...")
    print("\nNote: Make sure you have a Classification-formatted dataset in your Roboflow workspace")
    print("Popular datasets:")
    print("  • Livestock Disease Detection")
    print("  • Cattle Disease Classification")
    print("  • Bovine Disease Detection")
    
    project_name = input("\nEnter your Roboflow project name: ").strip()
    
    if not project_name:
        print("❌ Project name required!")
        exit(1)
    
    print(f"\n🔄 Accessing project: {project_name}")
    project = rf.workspace().project(project_name)
    
    # Download as Classification format
    print("\n⬇️  Downloading dataset (Classification format)...")
    
    # Clean up old datasets first
    if os.path.exists("c:/TROJAN/datasets/train"):
        print("🧹 Removing old dataset...")
        shutil.rmtree("c:/TROJAN/datasets/train")
    
    os.makedirs("c:/TROJAN/datasets", exist_ok=True)
    
    # Download with version=2 for classification
    dataset = project.version(2).download("classification", location="c:/TROJAN/datasets/train")
    
    print("\n✅ Dataset downloaded successfully!")
    print(f"📁 Location: c:/TROJAN/datasets/train")
    
    # Show what we got
    import os
    if os.path.exists("c:/TROJAN/datasets/train"):
        classes = [d for d in os.listdir("c:/TROJAN/datasets/train") if os.path.isdir(f"c:/TROJAN/datasets/train/{d}")]
        print(f"\n📂 Found {len(classes)} classes:")
        for cls in sorted(classes):
            cls_path = f"c:/TROJAN/datasets/train/{cls}"
            if os.path.isdir(cls_path):
                img_count = len([f for f in os.listdir(cls_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
                print(f"   • {cls}: {img_count} images")
    
    print("\n✅ Ready to train! Run this next:")
    print("   python better_train.py")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("  1. Check your API key is correct")
    print("  2. Make sure you have a Classification-format project in Roboflow")
    print("  3. Verify project name matches exactly")
    print("\nVisit: https://app.roboflow.com to manage your projects")
