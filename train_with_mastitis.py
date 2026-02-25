"""
Training script that integrates Mastitis disease detection with aggressive data augmentation.
Automatically handles train/validation split and includes Mastitis in the model.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, ConcatDataset
from torchvision import datasets, transforms, models
import os
import json
from pathlib import Path
import shutil

class MastitisAwareLivestockTrainer:
    def __init__(self, model_name="resnet50", num_classes=4, batch_size=32, learning_rate=0.001):
        """
        Initialize trainer with Mastitis support.
        
        Args:
            model_name: Model architecture (resnet50, resnet18, etc.)
            num_classes: Number of disease classes (should include Mastitis)
            batch_size: Batch size for training
            learning_rate: Learning rate for optimizer
        """
        self.model_name = model_name
        self.num_classes = num_classes
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"\n{'='*70}")
        print(f"Device: {self.device}")
        print(f"Model: {model_name}")
        print(f"Classes: {num_classes}")
        print(f"{'='*70}\n")
    
    def load_model(self):
        """Load pre-trained model with custom classification head."""
        print(f"Loading {self.model_name} model...")
        
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
        else:
            raise ValueError(f"Unknown model: {self.model_name}")
        
        return model.to(self.device)
    
    def get_data_transforms(self):
        """Return data augmentation transforms. Aggressive for small datasets like Mastitis."""
        # Aggressive augmentation for training - helps with small Mastitis dataset
        train_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.3),
            transforms.RandomRotation(30),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.8, 1.2)),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
            transforms.RandomPerspective(distortion_scale=0.2),
            transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Light augmentation for validation
        val_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        return train_transforms, val_transforms
    
    def prepare_data_from_folder_structure(self, root_path="datasets/train"):
        """
        Load data from folder structure: folder_name/class_name/ contains images.
        Automatically splits into train/val sets.
        """
        if not os.path.exists(root_path):
            print(f"❌ Dataset path not found: {root_path}")
            return None, None, None
        
        print(f"📁 Loading data from: {root_path}")
        
        train_transforms, val_transforms = self.get_data_transforms()
        
        # Load all data with train transforms first
        dataset = datasets.ImageFolder(root_path, transform=train_transforms)
        
        print(f"\n📊 Dataset Statistics:")
        print(f"   Total images: {len(dataset)}")
        print(f"   Classes found: {dataset.classes}")
        
        # Count images per class
        class_counts = {}
        for img_path, class_idx in dataset.imgs:
            class_name = dataset.classes[class_idx]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        print(f"\n   Per-class breakdown:")
        for class_name, count in class_counts.items():
            print(f"   - {class_name}: {count} images")
        
        # Check for Mastitis (very small dataset)
        if "Mastitis" in class_counts and class_counts["Mastitis"] < 50:
            print(f"\n⚠️  WARNING: Mastitis has only {class_counts['Mastitis']} images!")
            print(f"   Using aggressive data augmentation to compensate.")
        
        # Split into train/val (80/20)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
        
        # Create validation dataset with light transforms
        val_dataset_lite = datasets.ImageFolder(root_path, transform=val_transforms)
        _, val_dataset_lite = random_split(val_dataset_lite, [train_size, val_size])
        val_dataset = val_dataset_lite
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True
        )
        
        print(f"\n✓ Train samples: {len(train_dataset)}")
        print(f"✓ Val samples: {len(val_dataset)}")
        print(f"✓ Classes: {dataset.classes}")
        
        return train_loader, val_loader, dataset.classes
    
    def train_epoch(self, model, train_loader, criterion, optimizer):
        """Train for one epoch."""
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
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
            
            # Print progress every 10 batches
            if (batch_idx + 1) % 10 == 0:
                print(f"     Batch {batch_idx + 1}/{len(train_loader)}")
        
        avg_loss = total_loss / len(train_loader)
        accuracy = 100 * correct / total
        return avg_loss, accuracy
    
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
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100 * correct / total
        return avg_loss, accuracy
    
    def train(self, epochs=30, data_path="datasets/train"):
        """Train the model with Mastitis support."""
        print("\n" + "="*70)
        print("🚀 STARTING TRAINING WITH MASTITIS")
        print("="*70)
        
        # Load data
        result = self.prepare_data_from_folder_structure(data_path)
        if result is None:
            return
        
        train_loader, val_loader, class_names = result
        
        # Initialize model
        print(f"\n🔧 Initializing model...")
        model = self.load_model()
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, 'min', patience=5, factor=0.5
        )
        
        best_val_acc = 0
        best_epoch = 0
        os.makedirs("Models", exist_ok=True)
        
        print(f"\n📚 Training for {epochs} epochs...")
        print("="*70 + "\n")
        
        for epoch in range(epochs):
            print(f"Epoch [{epoch+1}/{epochs}]", end=" | ")
            
            train_loss, train_acc = self.train_epoch(model, train_loader, criterion, optimizer)
            val_loss, val_acc = self.validate(model, val_loader, criterion)
            scheduler.step(val_loss)
            
            print(f"\n  📊 Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}%")
            print(f"  📊 Val Loss:   {val_loss:.4f}, Acc: {val_acc:.2f}%")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_epoch = epoch + 1
                
                # Save checkpoint with class names
                checkpoint = {
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'accuracy': val_acc,
                    'class_names': list(class_names),
                    'num_classes': len(class_names),
                    'model_name': self.model_name
                }
                
                model_path = "Models/livestock_disease_detection.pth"
                torch.save(checkpoint, model_path)
                print(f"  ✅ Saved best model! ({val_acc:.2f}%)")
            else:
                print(f"  Current best: {best_val_acc:.2f}% (Epoch {best_epoch})")
            
            print()
        
        print("="*70)
        print(f"✅ Training Complete!")
        print(f"   Best Accuracy: {best_val_acc:.2f}% (Epoch {best_epoch})")
        print(f"   Model saved to: Models/livestock_disease_detection.pth")
        print(f"   Classes trained: {', '.join(class_names)}")
        print("="*70)
        
        return model


def main():
    print("\n" + "="*70)
    print("🐄 Mastitis-Aware Livestock Disease Detection Training")
    print("="*70)
    
    print("""
📋 This script trains a model that includes Mastitis detection.

📁 Dataset Structure Expected:
   datasets/train/
   ├── healthy/
   ├── lumpy/
   ├── foot-and-mouth/
   └── Mastitis/
       └── (images)

⚠️  Special handling:
   • Small Mastitis dataset? ✓ Aggressive augmentation applied
   • Automatic train/val split (80/20)
   • Saves best model automatically
   • Class names saved with model
""")
    
    # Initialize trainer with 4 classes (Healthy, Lumpy, Foot-and-mouth, Mastitis)
    trainer = MastitisAwareLivestockTrainer(
        model_name="resnet50",
        num_classes=4,  # Adjust based on your actual classes
        batch_size=16,  # Reduced for small datasets
        learning_rate=0.001
    )
    
    # Train
    try:
        trainer.train(epochs=40, data_path="datasets/train")
        print("\n✅ Training successful! Model is ready to use.")
    except KeyboardInterrupt:
        print("\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
