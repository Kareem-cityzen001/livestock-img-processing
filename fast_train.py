"""
Simple, fast training script for livestock disease detection.
Trains without interruption on small datasets.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
import os

print("\n" + "="*70)
print("LIVESTOCK DISEASE DETECTION - FAST TRAINING")
print("="*70)

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n✓ Using device: {device}")

# Load data
print(f"\nLoading images from: datasets/train")
dataset = datasets.ImageFolder("datasets/train", transform=transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
]))

# Split
val_size = max(1, len(dataset) // 5)
train_size = len(dataset) - val_size
train_data, val_data = random_split(dataset, [train_size, val_size])
val_data.dataset.transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print(f"✓ Total images: {len(dataset)}")
print(f"✓ Training: {train_size}, Validation: {val_size}")
print(f"✓ Diseases: {len(dataset.classes)}")
for i, name in enumerate(dataset.classes, 1):
    print(f"  {i}. {name}")

# Loaders
train_loader = DataLoader(train_data, batch_size=4, shuffle=True, num_workers=0)
val_loader = DataLoader(val_data, batch_size=4, shuffle=False, num_workers=0)

# Model
print("\n" + "-"*70)
print("Loading ResNet50...")
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.fc = nn.Linear(2048, len(dataset.classes))
model = model.to(device)
print(f"✓ Model ready with {len(dataset.classes)} output classes")

# Training
print("\n" + "-"*70)
print("Starting training (this will take a few minutes)...")
print("-"*70)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
best_loss = float('inf')
num_epochs = 15

for epoch in range(num_epochs):
    # Train
    model.train()
    train_loss, train_acc = 0, 0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
        train_acc += (outputs.argmax(1) == labels).sum().item()
    
    train_loss /= len(train_loader)
    train_acc = 100 * train_acc / train_size
    
    # Validate
    model.eval()
    val_loss, val_acc = 0, 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            val_loss += loss.item()
            val_acc += (outputs.argmax(1) == labels).sum().item()
    
    val_loss /= len(val_loader)
    val_acc = 100 * val_acc / val_size
    
    # Save best
    if val_loss < best_loss:
        best_loss = val_loss
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'accuracy': val_acc,
            'class_names': dataset.classes,
            'model_name': 'resnet50',
            'num_classes': len(dataset.classes)
        }
        torch.save(checkpoint, "Models/livestock_disease_detection.pth")
        print(f"Epoch {epoch+1:2d}/{num_epochs} | Train: {train_loss:.3f} ({train_acc:5.1f}%) | Val: {val_loss:.3f} ({val_acc:5.1f}%) ✓ SAVED")
    else:
        print(f"Epoch {epoch+1:2d}/{num_epochs} | Train: {train_loss:.3f} ({train_acc:5.1f}%) | Val: {val_loss:.3f} ({val_acc:5.1f}%)")

print("\n" + "="*70)
print("✓ TRAINING COMPLETE!")
print("="*70)
print(f"\n✓ Best model saved to: Models/livestock_disease_detection.pth")
print(f"✓ Final validation accuracy: {val_acc:.1f}%")
print("\nNext step:")
print("  1. Run web app: python app.py")
print("  2. Upload images to http://localhost:5000")
print("  3. See predictions with your trained model!")
