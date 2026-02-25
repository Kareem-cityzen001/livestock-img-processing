"""
Resume Mastitis training from last checkpoint.
Continues from where training was interrupted.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
import os
import time

class ResumeMastitisTrainer:
    def __init__(self, model_name="resnet50", num_classes=4, batch_size=8, learning_rate=0.001):
        """Resume trainer with checkpoint loading."""
        self.model_name = model_name
        self.num_classes = num_classes
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"\nResume Training Mode")
        print(f"Device: {self.device}")
        print(f"Model: {model_name}")
        print(f"Batch Size: {batch_size}")
    
    def load_model(self, checkpoint_path=None):
        """Load model from checkpoint or initialize new."""
        optimizer = None
        start_epoch = 0
        best_val_acc = 0
        class_names = None
        
        # Create model with correct num_classes
        model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, self.num_classes)
        model = model.to(self.device)
        
        optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)
        
        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                print(f"\n[*] Checking checkpoint: {checkpoint_path}")
                checkpoint = torch.load(checkpoint_path, map_location=self.device)
                checkpoint_classes = checkpoint.get('num_classes', 0)
                
                # Only load if class count matches
                if checkpoint_classes == self.num_classes:
                    print(f"[*] Loading checkpoint with {checkpoint_classes} classes")
                    model.load_state_dict(checkpoint['model_state_dict'])
                    
                    if 'optimizer_state_dict' in checkpoint:
                        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                    
                    start_epoch = checkpoint.get('epoch', 0) + 1
                    best_val_acc = checkpoint.get('accuracy', 0)
                    class_names = checkpoint.get('class_names', None)
                    
                    print(f"   Resuming from epoch {start_epoch}")
                    print(f"   Previous best accuracy: {best_val_acc:.1f}%")
                else:
                    print(f"[!] Class mismatch: checkpoint has {checkpoint_classes} classes")
                    print(f"[!] Current data has {self.num_classes} classes")
                    print(f"[!] Starting fresh training...")
            except Exception as e:
                print(f"[!] Error loading checkpoint: {e}")
                print(f"[!] Starting fresh training with {self.num_classes} classes...")
        else:
            print(f"\n[*] Starting fresh training with {self.num_classes} classes...")
        
        return model, optimizer, start_epoch, best_val_acc, class_names
    
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
        print(f"\nLoading from: {data_path}")
        
        train_transforms, val_transforms = self.get_data_transforms()
        dataset = datasets.ImageFolder(data_path, transform=train_transforms)
        
        print(f"Total images: {len(dataset)}")
        
        # Count per class
        class_counts = {}
        for _, class_idx in dataset.imgs:
            class_name = dataset.classes[class_idx]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        print(f"Classes: {', '.join(class_counts.keys())}")
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
            num_workers=0
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=0
        )
        
        print(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}")
        return train_loader, val_loader, dataset.classes
    
    def train_epoch(self, model, train_loader, criterion, optimizer):
        """Train one epoch."""
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        start_time = time.time()
        batch_count = len(train_loader)
        
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
            
            # Progress every 50 batches with more info
            if (batch_idx + 1) % 50 == 0:
                elapsed = time.time() - start_time
                percent_done = 100 * (batch_idx + 1) / batch_count
                print(f" {percent_done:.0f}%", end="", flush=True)
        
        print(" DONE", end="", flush=True)
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
    
    def train(self, epochs=10, data_path="datasets/train", checkpoint_path="Models/livestock_disease_detection.pth"):
        """Resume training from checkpoint."""
        print("\n" + "="*70)
        print("RESUMING MASTITIS TRAINING")
        print("="*70)
        
        # Load model and optimizer from checkpoint
        model, optimizer, start_epoch, best_val_acc, class_names = self.load_model(checkpoint_path)
        
        # Load data
        train_loader, val_loader, loaded_classes = self.load_data(data_path)
        
        if class_names is None:
            class_names = loaded_classes
        
        criterion = nn.CrossEntropyLoss()
        
        print(f"\nResuming training from epoch {start_epoch+1}/{epochs}...")
        print(f"Remaining epochs: {epochs - start_epoch}\n")
        
        for epoch in range(start_epoch, epochs):
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
                
                os.makedirs("Models", exist_ok=True)
                torch.save(checkpoint, checkpoint_path)
                print(f"  [+] Best model updated! ({val_acc:.1f}%)\n")
            else:
                print(f"  (Best so far: {best_val_acc:.1f}%)\n")
        
        print("="*70)
        print(f"TRAINING COMPLETE!")
        print(f"  Final Best Accuracy: {best_val_acc:.1f}%")
        print(f"  Model: {checkpoint_path}")
        print(f"  Classes: {', '.join(class_names)}")
        print("="*70)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("MASTITIS TRAINING RESUME")
    print("="*70)
    print("""
This script resumes training from your last checkpoint.
- If a checkpoint exists, it will continue from there
- Otherwise, it will start fresh
""")
    
    trainer = ResumeMastitisTrainer(
        model_name="resnet50",
        num_classes=4,
        batch_size=8,
        learning_rate=0.001
    )
    
    try:
        start = time.time()
        trainer.train(epochs=10, data_path="datasets/train")
        total_time = time.time() - start
        print(f"\nTotal time: {total_time/60:.1f} minutes")
        print("Training successful! Model ready to use.")
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
