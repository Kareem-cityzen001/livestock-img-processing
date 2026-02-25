"""
Quick training script for Mastitis - Fast version for testing and validation.
Reduces batch size and epochs for faster training on CPU.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
import os
import time

class QuickMastitisTrainer:
    def __init__(self, model_name="resnet50", num_classes=4, batch_size=8, learning_rate=0.001):
        """Quick trainer for fast iteration."""
        self.model_name = model_name
        self.num_classes = num_classes
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"\n⚡ QUICK TRAINING MODE (CPU Optimized)")
        print(f"Device: {self.device}")
        print(f"Model: {model_name}")
        print(f"Batch Size: {batch_size} (smaller = faster)")
    
    def load_model(self):
        """Load ResNet50 model."""
        model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, self.num_classes)
        return model.to(self.device)
    
    def get_data_transforms(self):
        """Data transforms with augmentation."""
        train_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(20),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        val_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        return train_transforms, val_transforms
    
    def load_data(self, data_path="datasets/train"):
        """Load and split data."""
        print(f"\n📁 Loading from: {data_path}")
        
        train_transforms, val_transforms = self.get_data_transforms()
        dataset = datasets.ImageFolder(data_path, transform=train_transforms)
        
        print(f"✓ Total images: {len(dataset)}")
        
        # Count per class
        class_counts = {}
        for _, class_idx in dataset.imgs:
            class_name = dataset.classes[class_idx]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        print(f"✓ Classes: {', '.join(class_counts.keys())}")
        for cls, cnt in class_counts.items():
            print(f"  - {cls}: {cnt}")
        
        # 80/20 split
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, _ = random_split(dataset, [train_size, val_size])
        
        # Create validation split with val transforms
        val_dataset = datasets.ImageFolder(data_path, transform=val_transforms)
        _, val_dataset = random_split(val_dataset, [train_size, val_size])
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0  # Important: 0 for Windows
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=0
        )
        
        print(f"✓ Train: {len(train_dataset)}, Val: {len(val_dataset)}")
        return train_loader, val_loader, dataset.classes
    
    def train_epoch(self, model, train_loader, criterion, optimizer):
        """Train one epoch."""
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        start_time = time.time()
        
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
            
            # Progress every 100 batches
            if (batch_idx + 1) % 100 == 0:
                elapsed = time.time() - start_time
                print(f"     [{batch_idx + 1}/{len(train_loader)}] Loss: {loss.item():.4f} (⏱️  {elapsed:.1f}s)")
        
        return total_loss / len(train_loader), 100 * correct / total
    
    def validate(self, model, val_loader, criterion):
        """Validate model."""
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
    
    def train(self, epochs=10, data_path="datasets/train"):
        """Train the model."""
        print("\n" + "="*70)
        print("🚀 QUICK MASTITIS TRAINING (Fast CPU Mode)")
        print("="*70)
        
        # Load data
        train_loader, val_loader, class_names = self.load_data(data_path)
        
        # Model
        print(f"\n🔧 Loading model...")
        model = self.load_model()
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)
        
        best_val_acc = 0
        os.makedirs("Models", exist_ok=True)
        
        print(f"\n📚 Training {epochs} epochs...\n")
        
        for epoch in range(epochs):
            print(f"Epoch [{epoch+1}/{epochs}] | ", end="", flush=True)
            
            train_start = time.time()
            train_loss, train_acc = self.train_epoch(model, train_loader, criterion, optimizer)
            train_time = time.time() - train_start
            
            val_start = time.time()
            val_loss, val_acc = self.validate(model, val_loader, criterion)
            val_time = time.time() - val_start
            
            print(f"\n  Train: Loss={train_loss:.4f}, Acc={train_acc:.1f}% ({train_time:.0f}s)")
            print(f"  Val:   Loss={val_loss:.4f}, Acc={val_acc:.1f}% ({val_time:.0f}s)")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
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
                print(f"  ✅ Best model saved! ({val_acc:.1f}%)\n")
            else:
                print(f"  (Best so far: {best_val_acc:.1f}%)\n")
        
        print("="*70)
        print(f"✅ Quick training complete!")
        print(f"   Best Val Accuracy: {best_val_acc:.1f}%")
        print(f"   Model: Models/livestock_disease_detection.pth")
        print(f"   Classes: {', '.join(class_names)}")
        print(f"   Ready to use in app.py!")
        print("="*70)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("⚡ QUICK MASTITIS TRAINER - Fast Iteration Version")
    print("="*70)
    print("""
Perfect for testing and quick validation!

Features:
  ✓ Smaller batch size (8) = faster processing
  ✓ Shorter training (10 epochs vs 40) 
  ✓ Automatic best model save
  ✓ Class names saved with model
  
After quick training:
  1. Run your app.py
  2. Test with Mastitis images
  3. If accuracy is good, run full_train.py for 40 epochs
  4. Or just use this model if it works well!
""")
    
    trainer = QuickMastitisTrainer(
        model_name="resnet50",
        num_classes=4,
        batch_size=8,  # Smaller for CPU
        learning_rate=0.001
    )
    
    try:
        start = time.time()
        trainer.train(epochs=10, data_path="datasets/train")
        total_time = time.time() - start
        print(f"\n⏱️  Total time: {total_time/60:.1f} minutes")
        print("\n✅ Training successful! Model ready to test in app.py")
    except KeyboardInterrupt:
        print("\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
