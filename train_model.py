"""
Training script for fine-tuning livestock disease detection model.
Supports ResNet and EfficientNet architectures.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os
import json
from pathlib import Path

class LivestockDiseaseTrainer:
    def __init__(self, model_name="resnet50", num_classes=3, batch_size=32, learning_rate=0.001):
        """
        Initialize trainer for livestock disease detection.
        
        Args:
            model_name: Model architecture (resnet18, resnet50, efficientnet_b0, efficientnet_b4)
            num_classes: Number of disease classes
            batch_size: Batch size for training
            learning_rate: Learning rate for optimizer
        """
        self.model_name = model_name
        self.num_classes = num_classes
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"Device: {self.device}")
        print(f"Model: {model_name}")
        print(f"Classes: {num_classes}")
    
    def load_model(self):
        """Load pre-trained model with custom classification head."""
        if self.model_name == "resnet50":
            model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, self.num_classes)
        elif self.model_name == "resnet18":
            model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, self.num_classes)
        elif self.model_name == "efficientnet_b4":
            model = models.efficientnet_b4(weights=models.EfficientNet_B4_Weights.DEFAULT)
            in_features = model.classifier[-1].in_features
            model.classifier[-1] = nn.Linear(in_features, self.num_classes)
        elif self.model_name == "efficientnet_b0":
            model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
            in_features = model.classifier[-1].in_features
            model.classifier[-1] = nn.Linear(in_features, self.num_classes)
        else:
            raise ValueError(f"Unknown model: {self.model_name}")
        
        return model.to(self.device)
    
    def get_data_transforms(self):
        """Return data augmentation transforms."""
        train_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(20),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
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
        
        return train_transforms, val_transforms
    
    def load_data(self, data_path="datasets"):
        """Load training and validation datasets."""
        if not os.path.exists(data_path):
            print(f"\n⚠️  Dataset directory not found: {data_path}")
            print("Create the following structure:")
            print(f"""
{data_path}/
├── train/
│   ├── Healthy/
│   ├── Mastitis/
│   └── Lumpy_Skin_Disease/
└── val/
    ├── Healthy/
    ├── Mastitis/
    └── Lumpy_Skin_Disease/
""")
            return None, None
        
        train_transforms, val_transforms = self.get_data_transforms()
        
        train_dataset = datasets.ImageFolder(
            os.path.join(data_path, "train"),
            transform=train_transforms
        )
        
        val_dataset = datasets.ImageFolder(
            os.path.join(data_path, "val"),
            transform=val_transforms
        )
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=2
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=2
        )
        
        print(f"\n✓ Train samples: {len(train_dataset)}")
        print(f"✓ Val samples: {len(val_dataset)}")
        print(f"✓ Classes: {train_dataset.classes}")
        
        return train_loader, val_loader, train_dataset.classes
    
    def train_epoch(self, model, train_loader, criterion, optimizer):
        """Train for one epoch."""
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for images, labels in train_loader:
            images, labels = images.to(self.device), labels.to(self.device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        return total_loss / len(train_loader), 100 * correct / total
    
    def validate(self, model, val_loader, criterion):
        """Evaluate model on validation set."""
        model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        return total_loss / len(val_loader), 100 * correct / total
    
    def train(self, epochs=20, data_path="datasets"):
        """Train the model."""
        print("\n" + "="*70)
        print("STARTING TRAINING")
        print("="*70)
        
        # Load data
        result = self.load_data(data_path)
        if result is None:
            return
        
        train_loader, val_loader, class_names = result
        
        # Initialize model
        model = self.load_model()
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3, verbose=True)
        
        best_val_acc = 0
        os.makedirs("Models", exist_ok=True)
        
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(model, train_loader, criterion, optimizer)
            val_loss, val_acc = self.validate(model, val_loader, criterion)
            scheduler.step(val_loss)
            
            print(f"\nEpoch [{epoch+1}/{epochs}]")
            print(f"  Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}%")
            print(f"  Val Loss:   {val_loss:.4f}, Acc: {val_acc:.2f}%")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                checkpoint = {
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'accuracy': val_acc,
                    'class_names': class_names,
                    'model_name': self.model_name
                }
                model_path = f"Models/livestock_disease_detection.pth"
                torch.save(checkpoint, model_path)
                print(f"  ✓ Saved best model: {model_path} ({val_acc:.2f}%)")
        
        print(f"\n✓ Training complete! Best accuracy: {best_val_acc:.2f}%")
        return model


if __name__ == "__main__":
    # Example usage
    print("\nLivestock Disease Detection - Training Script")
    print("-" * 70)
    print("""
Before running this script, prepare your dataset:

1. Create dataset structure:
   datasets/
   ├── train/
   │   ├── Healthy/
   │   │   └── image1.jpg, image2.jpg, ...
   │   ├── Lumpy_Skin_Disease/
   │   │   └── image1.jpg, image2.jpg, ...
   │   ├── Foot_Rot/
   │   │   └── image1.jpg, image2.jpg, ...
   │   ├── Mastitis/
   │   │   └── image1.jpg, image2.jpg, ...
   │   ├── Blackleg/
   │   │   └── image1.jpg, image2.jpg, ...
   │   ├── Anthrax_Disease/
   │   │   └── image1.jpg, image2.jpg, ...
   │   └── Tick_Borne_Fever/
   │       └── image1.jpg, image2.jpg, ...
   └── val/
       ├── Healthy/
       ├── Lumpy_Skin_Disease/
       ├── Foot_Rot/
       ├── Mastitis/
       ├── Blackleg/
       ├── Anthrax_Disease/
       └── Tick_Borne_Fever/

2. Run this script:
   python train_model.py

3. The trained model will be saved to:
   Models/livestock_disease_detection.pth

Supported diseases:
  1. Healthy
  2. Lumpy Skin Disease
  3. Foot Rot
  4. Mastitis
  5. Blackleg
  6. Anthrax Disease
  7. Tick-Borne Fever
""")
    
    # Initialize trainer with 7 disease classes
    trainer = LivestockDiseaseTrainer(
        model_name="resnet50",
        num_classes=7,  # Updated for 7 disease classes
        batch_size=32,
        learning_rate=0.001
    )
    
    # Train
    try:
        trainer.train(epochs=20, data_path="datasets")
    except KeyboardInterrupt:
        print("\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
