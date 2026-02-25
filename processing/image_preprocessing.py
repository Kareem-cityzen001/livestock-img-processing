import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np


def _read_with_pil(path):
    try:
        with Image.open(path) as im:
            im = im.convert('RGB')
            arr = np.array(im)
            return arr
    except Exception:
        return None


def preprocess_image(image_path):
    # Try OpenCV first (fast), fall back to PIL for edge cases (tiny or unusual PNGs)
    img = cv2.imread(image_path)
    if img is None:
        # Fallback to PIL
        img = _read_with_pil(image_path)
        if img is None:
            print(f"[WARNING] Could not read image: {image_path}")
            return None

    # Resize and convert to RGB
    try:
        img_resized = cv2.resize(img, (224, 224))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    except Exception:
        # If cv2 conversion fails (e.g., already RGB numpy array), handle with numpy
        try:
            from PIL import Image
            im = Image.fromarray(img).resize((224, 224)).convert('RGB')
            img_rgb = np.array(im)
        except Exception:
            print(f"[WARNING] Could not process image: {image_path}")
            return None

    # Convert to tensor with normalization
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    tensor_img = transform(img_rgb)  # Returns [3, 224, 224]
    return tensor_img  # Don't add batch dimension here - let detect_disease handle it

