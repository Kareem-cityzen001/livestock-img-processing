"""Quick test to verify data loading works"""
import torch
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
import time

print("Testing data loading...")

train_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("[*] Loading dataset from datasets/train...")
start = time.time()
dataset = datasets.ImageFolder("datasets/train", transform=train_transforms)
print(f"[*] Loaded {len(dataset)} images in {time.time()-start:.1f}s")

print(f"[*] Classes: {dataset.classes}")
print(f"\n[*] Creating DataLoader...")
start = time.time()
loader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=0)
print(f"[*] Created DataLoader in {time.time()-start:.1f}s")

print(f"\n[*] Loading first batch...")
start = time.time()
for images, labels in loader:
    print(f"[+] Got batch! Shape: {images.shape}, Labels: {labels}")
    print(f"[+] Loading took {time.time()-start:.1f}s")
    break

print("\n[OK] Data loading works!")
