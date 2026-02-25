"""
Better training with dropout and strong regularization to prevent overfitting.
This will make the model generalize better to new images.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
import os

print("\n" + "="*70)
print("LIVESTOCK DISEASE DETECTION - BETTER TRAINING WITH REGULARIZATION")
print("="*70)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n[OK] Using device: {device}")

# Load data with HEAVY augmentation
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomVerticalFlip(p=0.3),
    transforms.RandomRotation(30),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
    transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print(f"\nLoading images from: datasets/train")
dataset = datasets.ImageFolder("datasets/train", transform=train_transform)

val_size = max(1, len(dataset) // 5)
train_size = len(dataset) - val_size
train_data, val_data = random_split(dataset, [train_size, val_size])

# Update validation transforms
val_data.dataset.transform = val_transform

print(f"[OK] Total images: {len(dataset)}")
print(f"[OK] Training: {train_size}, Validation: {val_size}")
print(f"[OK] Diseases: {len(dataset.classes)}")
for i, name in enumerate(dataset.classes, 1):
    print(f"  {i}. {name}")

train_loader = DataLoader(train_data, batch_size=8, shuffle=True, num_workers=0)
val_loader = DataLoader(val_data, batch_size=8, shuffle=False, num_workers=0)

# Model with DROPOUT for regularization
print("\n" + "-"*70)
print("Loading ResNet50 with Dropout...")
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

# Add dropout before and after final layer
model.fc = nn.Sequential(
    nn.Dropout(0.5),  # 50% dropout
    nn.Linear(2048, 512),
    nn.ReLU(),
    nn.Dropout(0.5),  # 50% dropout
    nn.Linear(512, len(dataset.classes))
)
model = model.to(device)
print(f"[OK] Model ready with strong regularization")

# Training with L2 regularization
print("\n" + "-"*70)
print("Starting training with regularization...")
print("-"*70)

criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=0.0005, weight_decay=0.01)  # L2 regularization
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=20)

best_loss = float('inf')
best_val_acc = 0
num_epochs = 20

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
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)  # Gradient clipping
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
    
    # Save best model
    if val_acc > best_val_acc or val_loss < best_loss:
        best_val_acc = val_acc
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
        print(f"Epoch {epoch+1:2d}/{num_epochs} | Train: {train_loss:.3f} ({train_acc:5.1f}%) | Val: {val_loss:.3f} ({val_acc:5.1f}%) **SAVED**")
    else:
        print(f"Epoch {epoch+1:2d}/{num_epochs} | Train: {train_loss:.3f} ({train_acc:5.1f}%) | Val: {val_loss:.3f} ({val_acc:5.1f}%)")
    
    scheduler.step()

print("\n" + "="*70)
print("[OK] TRAINING COMPLETE!")
print("="*70)
print(f"\n[OK] Best model saved with {best_val_acc:.1f}% validation accuracy")
print("\nImportant Note:")
print("  Your model still has limited real images (only 16 originals + augmentations)")
print("  For 95%+ accuracy, you need:")
print("    - 50+ real, diverse images per disease")
print("    - Different angles, lighting, severe/mild cases")
print("\n  Visit: https://universe.roboflow.com/ for free livestock disease datasets")
print("\nTest web app: python app.py")
