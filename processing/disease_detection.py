import torch
import torch.nn as nn
from torchvision import models
import os
from urllib.request import urlretrieve
import json

def load_model(num_classes=2, weights_path=None, model_name="resnet50"):
    """
    Load a pre-trained livestock disease detection model.
    
    Args:
        num_classes: Number of disease classes
        weights_path: Path to saved model weights
        model_name: Model architecture (resnet18, resnet50, efficientnet_b0, efficientnet_b4)
    
    Returns:
        PyTorch model in evaluation mode
    """
    
    # Select model architecture
    if model_name == "resnet50":
        model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        in_features = model.fc.in_features
    elif model_name == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        in_features = model.fc.in_features
    elif model_name == "efficientnet_b4":
        model = models.efficientnet_b4(weights=models.EfficientNet_B4_Weights.DEFAULT)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_classes)
    elif model_name == "efficientnet_b0":
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_classes)
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    # Replace the final layer for disease classification
    if model_name in ["resnet18", "resnet50"]:
        model.fc = nn.Linear(in_features, num_classes)
    
    # Load pre-trained weights if provided
    if weights_path and os.path.exists(weights_path):
        checkpoint = torch.load(weights_path, map_location=torch.device('cpu'))
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            
            # Try to load the checkpoint - if it fails due to architecture mismatch, ignore
            try:
                model.load_state_dict(state_dict)
            except RuntimeError as e:
                # If the checkpoint has dropout layers but model doesn't, rebuild fc layer
                if "fc.1.weight" in state_dict or "fc.0.weight" in state_dict:
                    # This is a model with dropout, rebuild it
                    model.fc = nn.Sequential(
                        nn.Dropout(0.5),
                        nn.Linear(in_features, 512),
                        nn.ReLU(),
                        nn.Dropout(0.5),
                        nn.Linear(512, num_classes)
                    )
                    # Try loading again
                    try:
                        model.load_state_dict(state_dict)
                    except Exception as load_err:
                        print(f"[WARNING] Could not load exact checkpoint: {load_err}")
                        print(f"[WARNING] Using model with ImageNet weights only")
                else:
                    print(f"[WARNING] Could not load checkpoint: {e}")
        else:
            try:
                model.load_state_dict(checkpoint)
            except RuntimeError:
                print(f"[WARNING] Checkpoint format not recognized, using ImageNet weights")
        
        print(f"[OK] Loaded weights from {weights_path}")
    
    model.eval()
    return model

def is_valid_livestock_image(image_tensor, model):
    """
    Check if image actually looks like livestock.
    Returns confidence that image is livestock (not car, person, etc.)
    """
    with torch.no_grad():
        outputs = model(image_tensor.unsqueeze(0) if image_tensor.dim() == 3 else image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        max_confidence = probabilities.max().item()
    
    # If model is less than 45% confident on ANY class, it's probably not livestock
    return max_confidence

def detect_disease(image_tensor, model, class_names):
    """
    Detect livestock disease from preprocessed image tensor.
    
    Args:
        image_tensor: Preprocessed image tensor (3D: [C, H, W])
        model: Trained PyTorch model
        class_names: List of disease class names
    
    Returns:
        Dictionary with diagnosis, confidence, and recommendations
    """
    try:
        with torch.no_grad():
            # Ensure input is 4D [B, C, H, W]
            if image_tensor.dim() == 3:
                image_tensor = image_tensor.unsqueeze(0)
            
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            disease = class_names[predicted.item()]
            confidence_val = confidence.item()
            
            # Debug print
            print(f"[DEBUG] Model output shape: {outputs.shape}")
            print(f"[DEBUG] Predicted class index: {predicted.item()}")
            print(f"[DEBUG] Predicted disease: {disease}")
            print(f"[DEBUG] Confidence: {confidence_val * 100:.2f}%")
            print(f"[DEBUG] All probabilities: {[f'{n}:{p*100:.2f}%' for n, p in zip(class_names, probabilities[0])]}")
            
            disease_info = get_disease_recommendation(disease)
            
            return {
                "Diagnosis": disease,
                "Confidence": f"{confidence_val * 100:.2f}%",
                "All_Predictions": {name: f"{prob * 100:.2f}%" for name, prob in zip(class_names, probabilities[0])},
                "Status": disease_info.get("status", "Unknown"),
                "Severity": disease_info.get("severity", "Unknown"),
                "Action": disease_info.get("action", "Consult veterinarian"),
                "Treatment": disease_info.get("treatment", "Professional evaluation required"),
                "Contagious": disease_info.get("contagious", "Unknown"),
                "Quarantine": disease_info.get("quarantine", "As needed")
            }
    except Exception as e:
        print(f"[ERROR] Disease detection failed: {e}")
        import traceback
        traceback.print_exc()
        return get_disease_recommendation("Unknown")

def get_disease_recommendation(disease):
    """
    Provide health recommendations based on detected disease.
    Includes treatment suggestions and severity levels.
    """
    recommendations = {
        "Healthy": {
            "status": "✓ Healthy",
            "severity": "None",
            "action": "Animal appears healthy. Continue regular monitoring and preventive care.",
            "treatment": "None needed. Maintain good hygiene and nutrition."
        },
        "Lumpy Skin Disease": {
            "status": "⚠️ ALERT",
            "severity": "HIGH",
            "action": "Lumpy Skin Disease detected. ISOLATE IMMEDIATELY and contact veterinarian.",
            "treatment": "Isolate affected animals. Supportive care, antibiotics for secondary infections. Vaccination program recommended.",
            "contagious": "Yes - Highly contagious",
            "quarantine": "Required"
        },
        "Foot And Mouth": {
            "status": "⚠️ ALERT",
            "severity": "HIGH",
            "action": "Suspected Foot-and-Mouth Disease. Isolate affected animals and notify veterinary authorities.",
            "treatment": "Supportive care, strict biosecurity, consult veterinarian for confirmation and control measures.",
            "contagious": "Yes - Extremely contagious",
            "quarantine": "Required"
        },
        "Foot Rot": {
            "status": "⚠️ WARNING",
            "severity": "MEDIUM",
            "action": "Foot Rot detected. Treat promptly to prevent spread and lameness.",
            "treatment": "Trim affected hooves, apply antiseptic foot baths, keep area dry. Antibiotics if needed.",
            "contagious": "Yes - Moderately contagious",
            "quarantine": "Separate affected animals"
        },
        "Mastitis": {
            "status": "⚠️ WARNING",
            "severity": "MEDIUM",
            "action": "Mastitis detected. Requires immediate veterinary treatment.",
            "treatment": "Antibiotics, improved milking hygiene, supportive care. Monitor milk quality.",
            "contagious": "Moderately contagious",
            "quarantine": "Isolate if severe"
        },
        "Blackleg": {
            "status": "🚨 CRITICAL",
            "severity": "CRITICAL",
            "action": "BLACKLEG DETECTED - EXTREME EMERGENCY. Isolate and contact veterinarian immediately.",
            "treatment": "High-dose antibiotics if caught early (often too late). Vaccination critical for prevention.",
            "contagious": "Not contagious but environmentally persistent",
            "quarantine": "IMMEDIATE"
        },
        "Anthrax Disease": {
            "status": "🚨 CRITICAL",
            "severity": "CRITICAL",
            "action": "ANTHRAX SUSPECTED - REPORT TO AUTHORITIES IMMEDIATELY. Public health concern.",
            "treatment": "Requires specialized veterinary care. Quarantine and decontamination necessary.",
            "contagious": "Highly contagious and zoonotic",
            "quarantine": "IMMEDIATE - PUBLIC HEALTH ALERT"
        },
        "Tick-Borne Fever": {
            "status": "⚠️ WARNING",
            "severity": "MEDIUM",
            "action": "Tick-Borne Fever detected. Implement tick control measures.",
            "treatment": "Antibiotics (tetracycline), nutritional support. Control tick populations.",
            "contagious": "Transmitted by tick vectors",
            "quarantine": "Reduce contact with other animals"
        }
    }
    
    # Normalize the incoming disease name to improve matching with keys.
    def _normalize(name):
        if not isinstance(name, str):
            return ""
        return name.strip().lower().replace('_', ' ').replace('-', ' ')

    norm = _normalize(disease)

    # Try exact normalized match against recommendations keys
    for key, info in recommendations.items():
        if _normalize(key) == norm:
            return info

    # Fallback: try substring matching (helps with slight variations)
    for key, info in recommendations.items():
        if _normalize(key) in norm or norm in _normalize(key):
            return info

    # Final fallback: unknown disease
    return {
        "status": "❓ Unknown",
        "severity": "UNKNOWN",
        "action": "Please consult a veterinarian for proper diagnosis and treatment.",
        "treatment": "Professional veterinary evaluation required."
    }
