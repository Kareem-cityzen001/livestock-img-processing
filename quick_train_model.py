"""
Quick training script to train the livestock disease detection model.
Creates synthetic training data for demonstration and trains the model.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torchvision import models, transforms
import numpy as np
import os
from pathlib import Path

def create_synthetic_training_data(num_samples_per_class=10):
    """
    Create synthetic training data for demonstration.
    In production, you would use real livestock disease images.
    """
    print(f"Creating synthetic training data ({num_samples_per_class} samples per class)...")
    
    class_names = [
        "Healthy",
        "Lumpy Skin Disease",
        "Foot Rot",
        "Mastitis",
        "Blackleg",
        "Anthrax Disease",
        "Tick-Borne Fever"
    ]
    
    # Create synthetic images (random tensors normalized like image data)
    X_train = []
    y_train = []
    
    for class_idx, disease in enumerate(class_names):
        for _ in range(num_samples_per_class):
            # Create random synthetic image in shape [3, 224, 224]
            synthetic_image = torch.randn(3, 224, 224)
            # Normalize to ImageNet stats
            normalize = transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
            synthetic_image = normalize(synthetic_image)
            
            X_train.append(synthetic_image)
            y_train.append(class_idx)
    
    X_train = torch.stack(X_train)
    y_train = torch.tensor(y_train, dtype=torch.long)
    
    print(f"✓ Created {len(X_train)} synthetic images across {len(class_names)} classes")
    return X_train, y_train, class_names

def train_livestock_disease_model():
    print("\n" + "="*70)
    print("LIVESTOCK DISEASE DETECTION - MODEL TRAINING")
    print("="*70)
    
    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n✓ Using device: {device}")
    
    # Create synthetic data for training
    X_train, y_train, class_names = create_synthetic_training_data(num_samples_per_class=15)
    
    # Create dataset and dataloader
    dataset = TensorDataset(X_train, y_train)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
    
    print(f"\nDisease Classes ({len(class_names)}):")
    for i, disease in enumerate(class_names, 1):
        print(f"  {i}. {disease}")
    
    # Load ResNet50 model
    print("\n" + "-"*70)
    print("Loading model...")
    model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, len(class_names))
    model = model.to(device)
    print(f"✓ ResNet50 loaded with {len(class_names)} output classes")
    
    # Training setup
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    num_epochs = 10
    
    # Training loop
    print("\n" + "-"*70)
    print("Starting training...")
    print("-"*70)
    
    model.train()
    for epoch in range(num_epochs):
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(dataloader):
            images = images.to(device)
            labels = labels.to(device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        avg_loss = total_loss / len(dataloader)
        
        print(f"Epoch [{epoch+1}/{num_epochs}] Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
    
    # Save trained model
    print("\n" + "-"*70)
    print("Saving trained model...")
    os.makedirs("Models", exist_ok=True)
    
    checkpoint = {
        'epoch': num_epochs,
        'model_state_dict': model.state_dict(),
        'accuracy': accuracy,
        'class_names': class_names,
        'model_name': 'resnet50',
        'num_classes': len(class_names)
    }
    
    model_path = "Models/livestock_disease_detection.pth"
    torch.save(checkpoint, model_path)
    
    file_size = os.path.getsize(model_path) / (1024**2)
    print(f"✓ Model saved to: {model_path}")
    print(f"✓ Model size: {file_size:.1f} MB")
    print(f"✓ Final accuracy on training set: {accuracy:.2f}%")
    
    # Test the model
    print("\n" + "="*70)
    print("TESTING TRAINED MODEL")
    print("="*70)
    
    model.eval()
    with torch.no_grad():
        # Test on first batch
        test_images, test_labels = next(iter(dataloader))
        test_images = test_images.to(device)
        
        outputs = model(test_images)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        
        for i in range(min(3, len(test_images))):
            predicted_class = probabilities[i].argmax().item()
            confidence = probabilities[i].max().item() * 100
            true_class = test_labels[i].item()
            
            print(f"\nSample {i+1}:")
            print(f"  Predicted: {class_names[predicted_class]} ({confidence:.2f}%)")
            print(f"  Actual: {class_names[true_class]}")
            print(f"  All predictions: {', '.join([f'{cn}:{p*100:.1f}%' for cn, p in zip(class_names, probabilities[i])])}")
    
    print("\n" + "="*70)
    print("✓ TRAINING COMPLETE!")
    print("="*70)
    print("\nYour model has been trained and saved.")
    print("Now test it in the web app: http://localhost:5000")

if __name__ == "__main__":
    train_livestock_disease_model()
