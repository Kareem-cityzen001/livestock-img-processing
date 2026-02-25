"""
Real-world training script for livestock disease detection.
This script shows how to train on actual disease images if you have them.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os

def train_on_real_data(data_path="datasets", val_split=0.2):
    """
    Train the model on real livestock disease images.
    
    Automatically splits training data into train/val sets.
    
    Expected directory structure:
    datasets/
    ├── train/
    │   ├── Healthy/
    │   ├── Lumpy_Skin_Disease/
    │   ├── Foot_Rot/
    │   ├── Mastitis/
    │   ├── Blackleg/
    │   ├── Anthrax_Disease/
    │   └── Tick_Borne_Fever/
    └── val/  (optional - will be created if missing)
        └── (same structure)
    """
    from torch.utils.data import random_split
    
    print("\n" + "="*70)
    print("LIVESTOCK DISEASE DETECTION - REAL DATA TRAINING")
    print("="*70)
    
    # Check if data exists
    if not os.path.exists(data_path):
        print(f"\n✗ Dataset directory not found: {data_path}")
        print("\nTo train the model, create this structure:")
        print("""
datasets/
├── train/
│   ├── Healthy/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   ├── Lumpy_Skin_Disease/
│   ├── Foot_Rot/
│   ├── Mastitis/
│   ├── Blackleg/
│   ├── Anthrax_Disease/
│   └── Tick_Borne_Fever/

Then run: python train_on_real_data.py
        """)
        
        print("\nAlternatively, get free datasets from:")
        print("  • Roboflow: https://universe.roboflow.com/")
        print("  • Kaggle: https://www.kaggle.com/")
        print("  • Google Open Images: https://storage.googleapis.com/openimages/web/index.html")
        return
    
    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n✓ Using device: {device}")
    
    # Data transforms
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    # Load full training dataset
    print(f"\nLoading images from: {data_path}/train")
    full_dataset = datasets.ImageFolder(f"{data_path}/train", transform=train_transforms)
    
    # Automatically split into train/val
    val_size = int(len(full_dataset) * val_split)
    train_size = len(full_dataset) - val_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    # Apply validation transforms to validation set
    val_dataset.dataset.transform = val_transforms
    train_dataset.dataset.transform = train_transforms
    
    print(f"✓ Training samples: {train_size}")
    print(f"✓ Validation samples: {val_size}")
    print(f"✓ Disease classes: {len(full_dataset.classes)}")
    for i, disease in enumerate(full_dataset.classes, 1):
        print(f"  {i}. {disease}")
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=0)
    
    # Load model
    print("\n" + "-"*70)
    print("Loading ResNet50 model...")
    model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, len(full_dataset.classes))
    model = model.to(device)
    print(f"✓ Model loaded with {len(full_dataset.classes)} output classes")
    
    # Training setup
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', factor=0.5, patience=5)
    
    num_epochs = 20
    best_val_loss = float('inf')
    
    # Training loop
    print("\n" + "-"*70)
    print("Starting training...")
    print("-"*70)
    
    for epoch in range(num_epochs):
        # Train
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        # Validate
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        train_acc = 100 * train_correct / train_total
        val_acc = 100 * val_correct / val_total
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        
        print(f"Epoch [{epoch+1}/{num_epochs}]")
        print(f"  Train Loss: {avg_train_loss:.4f}, Acc: {train_acc:.2f}%")
        print(f"  Val Loss:   {avg_val_loss:.4f}, Acc: {val_acc:.2f}%")
        
        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'accuracy': val_acc,
                'class_names': full_dataset.classes,
                'model_name': 'resnet50',
                'num_classes': len(full_dataset.classes)
            }
            torch.save(checkpoint, "Models/livestock_disease_detection.pth")
            print(f"  ✓ Model saved (best validation loss)")
        
        scheduler.step(avg_val_loss)
    
    print("\n" + "="*70)
    print("✓ TRAINING COMPLETE!")
    print("="*70)
    print(f"\nBest model saved to: Models/livestock_disease_detection.pth")
    print("Test it with: python test_model.py")
    print("Or run the web app: python app.py")

if __name__ == "__main__":
    train_on_real_data()
