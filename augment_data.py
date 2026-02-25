"""
Data Augmentation - Create more training images from your existing ones.
This helps the model generalize better instead of just memorizing.
"""

import cv2
import os
import numpy as np
from pathlib import Path

def augment_image(image_path, output_dir, num_variations=15):
    """Create multiple variations of one image through augmentation."""
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"✗ Could not read: {image_path}")
        return 0
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(image_path).stem
    count = 0
    
    # Original
    cv2.imwrite(f"{output_dir}/{base_name}_001.jpg", img)
    count += 1
    
    # Rotations
    for angle in [-25, -15, -5, 5, 15, 25]:
        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h))
        cv2.imwrite(f"{output_dir}/{base_name}_rot{angle:+d}_{count:03d}.jpg", rotated)
        count += 1
    
    # Brightness adjustments
    for brightness in [-40, -20, 20, 40]:
        adjusted = cv2.convertScaleAbs(img.astype(np.float32) * 1.0 + brightness)
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        cv2.imwrite(f"{output_dir}/{base_name}_bright{brightness:+d}_{count:03d}.jpg", adjusted)
        count += 1
    
    # Flips
    flipped_h = cv2.flip(img, 1)  # Horizontal
    cv2.imwrite(f"{output_dir}/{base_name}_fliph_{count:03d}.jpg", flipped_h)
    count += 1
    
    flipped_v = cv2.flip(img, 0)  # Vertical
    cv2.imwrite(f"{output_dir}/{base_name}_flipv_{count:03d}.jpg", flipped_v)
    count += 1
    
    return count

# Main augmentation
print("\n" + "="*70)
print("DATA AUGMENTATION - Creating More Training Images")
print("="*70)

data_path = "datasets/train"
diseases = os.listdir(data_path)

total_created = 0

for disease in sorted(diseases):
    disease_path = os.path.join(data_path, disease)
    if not os.path.isdir(disease_path):
        continue
    
    images = [f for f in os.listdir(disease_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    print(f"\n{disease}:")
    print(f"  Original images: {len(images)}")
    
    created_count = 0
    for img_file in images:
        img_path = os.path.join(disease_path, img_file)
        new_count = augment_image(img_path, disease_path, num_variations=15)
        created_count += new_count
    
    print(f"  Total after augmentation: {created_count}")
    total_created += created_count

print("\n" + "="*70)
print(f"✓ AUGMENTATION COMPLETE!")
print(f"✓ Total images created: {total_created}")
print("="*70)

print(f"\n✓ New training data ready at: {data_path}")
print("\nNext step: Train the model again")
print("  Run: python fast_train.py")
print("\nYour model will now learn better patterns instead of memorizing!")
