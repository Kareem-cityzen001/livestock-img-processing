"""
Training script with explicit output flushing for visible progress on terminal.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
import sys
import os

def flush_print(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

flush_print("\n" + "="*70)
flush_print("LIVESTOCK DISEASE DETECTION - TRAINING WITH VISIBLE PROGRESS")
flush_print("="*70)

device = torch.device("cpu")
flush_print(f"\n[OK] Using device: {device}")

# Load data
flush_print(f"[..] Loading images from: datasets/train")
dataset = datasets.ImageFolder("datasets/train", transform=transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
]))

val_size = max(1, len(dataset) // 5)
train_size = len(dataset) - val_size
train_data, val_data = random_split(dataset, [train_size, val_size])
val_data.dataset.transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

flush_print(f"[OK] Total images: {len(dataset)}")
flush_print(f"[OK] Training: {train_size}, Validation: {val_size}")
flush_print(f"[OK] Diseases: {len(dataset.classes)}")
for i, name in enumerate(dataset.classes, 1):
    flush_print(f"     {i}. {name}")

train_loader = DataLoader(train_data, batch_size=4, shuffle=True, num_workers=0)
val_loader = DataLoader(val_data, batch_size=4, shuffle=False, num_workers=0)

flush_print(f"\n[..] Loading ResNet50...")
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.fc = nn.Linear(2048, len(dataset.classes))
model = model.to(device)
flush_print(f"[OK] Model ready")

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
best_val_acc = 0

num_epochs = 15
flush_print(f"\n[..] Starting {num_epochs}-epoch training...")
flush_print("-"*70)
sys.stdout.flush()

for epoch in range(num_epochs):
    model.train()
    train_loss, train_acc, train_count = 0, 0, 0
    
    for batch_idx, (images, labels) in enumerate(train_loader):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
        train_acc += (outputs.argmax(1) == labels).sum().item()
        train_count += labels.size(0)
    
    train_loss /= len(train_loader)
    train_acc_pct = 100 * train_acc / train_size
    
    # Validate
    model.eval()
    val_loss, val_acc, val_count = 0, 0, 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            val_acc += (outputs.argmax(1) == labels).sum().item()
            val_count += labels.size(0)
    
    val_loss /= len(val_loader)
    val_acc_pct = 100 * val_acc / val_size
    
    # Save if best
    if val_acc_pct > best_val_acc:
        best_val_acc = val_acc_pct
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'accuracy': val_acc_pct,
            'class_names': list(dataset.classes),
            'model_name': 'resnet50',
            'num_classes': len(dataset.classes)
        }, 'Models/livestock_disease_detection.pth')
        marker = "[SAVED]"
    else:
        marker = ""
    
    flush_print(f"Epoch {epoch+1:2d}/{num_epochs} | Train: {train_loss:.3f} ({train_acc_pct:5.1f}%) | Val: {val_loss:.3f} ({val_acc_pct:5.1f}%) {marker}")
    sys.stdout.flush()
    
    scheduler.step()

flush_print("\n" + "="*70)
flush_print(f"[DONE] Best validation accuracy: {best_val_acc:.1f}%")
flush_print(f"[DONE] Model saved to: Models/livestock_disease_detection.pth")
flush_print("="*70)
flush_print("\nRestart Flask app to test: python app.py")
sys.stdout.flush()
