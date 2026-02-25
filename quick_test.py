import torch
from processing.disease_detection import load_model, detect_disease
from processing.image_preprocessing import preprocess_image
import os

class_names = ['Healthy', 'Lumpy Skin Disease', 'Foot Rot', 'Mastitis', 'Blackleg', 'Anthrax Disease', 'Tick-Borne Fever']
model = load_model(num_classes=7, weights_path='Models/livestock_disease_detection.pth', model_name='resnet50')

print("Testing trained model on sample images...\n")

# Test on images from each disease
test_images = [
    'datasets/train/Foot_Rot/image1.jpg',
    'datasets/train/Foot_Rot/image2.jpg',
    'datasets/train/Lumpy_Skin_Disease/image1.jpg',
    'datasets/train/Healthy/image1.jpg',
]

for test_image in test_images:
    if os.path.exists(test_image):
        img = preprocess_image(test_image)
        result = detect_disease(img, model, class_names)
        print(f"Image: {test_image}")
        print(f"  Predicted: {result['Diagnosis']} ({result['Confidence']})")
        print()
