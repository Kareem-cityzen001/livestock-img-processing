# Mastitis Dataset Training Guide

## ✅ Dataset Status

Your Mastitis dataset has been successfully added and contains:
- **Mastitis images**: 4,897 (60% of your dataset!)
- **Healthy images**: 1,291
- **Lumpy images**: 1,207
- **Foot-and-mouth images**: 746
- **Total**: 8,141 images

Excellent coverage for training!

---

## 🚀 Training Options Available

### **Option 1: Quick Training (⚡ Recommended for Testing)**
```bash
python quick_train_mastitis.py
```
- ⏱️ **Time**: ~30-45 minutes on CPU
- 📊 **Epochs**: 10
- 🎯 **Purpose**: Test model quality before full training
- ✅ **Best for**: Quick validation and testing

### **Option 2: Full Training (🎓 Production Quality)**
```bash
python train_with_mastitis.py
```
- ⏱️ **Time**: 3-6 hours on CPU (30 mins on GPU)
- 📊 **Epochs**: 40
- 🎯 **Purpose**: Maximum accuracy
- ✅ **Best for**: Production deployment

### **Option 3: Original Training Script (Legacy)**
```bash
python train_model.py
```
- Original script - works but requires manual setup
- Use if you need specific configuration

---

## 📊 What Gets Trained

Both scripts will automatically:

1. **Load all 4 disease classes**
   - Mastitis (4,897 images) ← NEW!
   - Healthy (1,291 images)
   - Lumpy Skin Disease (1,207 images)
   - Foot-and-mouth (746 images)

2. **Split data automatically**
   - 80% training (6,512 images)
   - 20% validation (1,629 images)

3. **Apply data augmentation**
   - Rotation, flip, color jitter
   - Helps improve model generalization

4. **Save best model**
   - Automatically updates: `Models/livestock_disease_detection.pth`
   - Saves class order with model
   - Ready for app.py to use

---

## 🎯 Model Architecture

**ResNet50**
- Pre-trained on ImageNet
- Fine-tuned on your livestock diseases (including Mastitis!)
- 224x224 image input
- 4-class output (Mastitis, Healthy, Lumpy, Foot-and-mouth)

**Why ResNet50?**
- Excellent accuracy for medical imaging
- Fast inference (good for mobile)
- Transfer learning works well with your dataset size

---

## 📈 Expected Performance

Based on dataset size and classes:

| Stage | Expected Accuracy |
|-------|------------------|
| After epoch 1 | 60-70% |
| After epoch 5 | 80-85% |
| After epoch 10 | 85-90% |
| After epoch 40 | 90-95% |

**Mastitis Detection**: Should be very high accuracy given you have 4,897 training images

---

## 🔄 Training Workflow

### **First Time: Quick Validation**
```
1. python quick_train_mastitis.py    # 30-45 min
2. Test with app.py
3. If accuracy looks good → continue
4. If accuracy needs improvement → full training
```

### **Production Ready: Full Training**
```
1. python train_with_mastitis.py     # 3-6 hours
2. Takes a break, grab coffee ☕
3. Returns with best model trained
4. Deploy to app.py
```

---

## 🛠️ Customization Options

### Modify training parameters in scripts:

**quick_train_mastitis.py:**
```python
trainer = QuickMastitisTrainer(
    model_name="resnet50",      # Can change to resnet18
    num_classes=4,              # Number of disease classes
    batch_size=8,               # Smaller = slower but less memory
    learning_rate=0.001         # Learning rate
)
trainer.train(epochs=10)        # Number of epochs
```

**train_with_mastitis.py:**
```python
trainer = MastitisAwareLivestockTrainer(
    model_name="resnet50",
    num_classes=4,
    batch_size=16,              # Can increase to 32 if memory allows
    learning_rate=0.001
)
trainer.train(epochs=40)        # Full 40 epochs
```

---

## 📊 Understanding Training Output

When training runs, you'll see:

```
Epoch [1/10] | 
  Train: Loss=0.8234, Acc=65.3% (120s)
  Val:   Loss=0.7891, Acc=72.1% (30s)
  ✅ Best model saved! (72.1%)

Epoch [2/10] | 
  Train: Loss=0.5623, Acc=78.5% (120s)
  Val:   Loss=0.4932, Acc=81.2% (30s)
  ✅ Best model saved! (81.2%)
```

**What this means:**
- **Train Loss**: Gets lower = learning
- **Train Acc**: Should increase = improving
- **Val Acc**: What matters for real accuracy
- **✅ Best model saved**: Checkpoint updated

---

## ✅ After Training Complete

When you see:
```
✅ Training successful! Model ready to test in app.py
```

The model is saved at:
```
Models/livestock_disease_detection.pth
```

**Your app.py automatically uses this!** Just restart `app.py` and:
1. Upload an image
2. Add behavioral description (optional)
3. Click "Analyze Health Condition"
4. Get diagnosis including Mastitis detection!

---

## 🐛 Troubleshooting

### **Training is slow**
- Normal on CPU! 
- Grab coffee ☕ while it runs
- First epoch is always slowest due to caching

### **Out of memory errors**
- Reduce batch_size: 16 → 8 or 4
- More data augmentation is applied instead

### **Model not improving after epoch 5**
- Normal! Learning rate might adjust
- Keep training - best models take time
- ReduceLROnPlateau will reduce learning rate if needed

### **Can't find dataset**
- Verify structure:
  ```
  c:\TROJAN\datasets\train\
  ├── Mastitis\
  ├── healthy\
  ├── lumpy\
  └── foot-and-mouth\
  ```

---

## 🔍 Verifying Mastitis in Model

After training, verify Mastitis is included:

```python
import torch

checkpoint = torch.load('Models/livestock_disease_detection.pth')
classes = checkpoint['class_names']
print(classes)
# Should output: ['Mastitis', 'foot-and-mouth', 'healthy', 'lumpy']
```

**✅ Mastitis is class index 0!**

---

## 📝 Advanced: GPU Training (Faster)

If you have an NVIDIA GPU:

```bash
# Install GPU PyTorch (one time)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Then run normal training
python train_with_mastitis.py
```

Times on GPU:
- Quick training: 5-10 minutes
- Full training: 30-60 minutes

---

## 📞 Summary Checklist

- [x] Mastitis dataset added (4,897 images)
- [x] Training scripts created
- [x] Automatic data splitting
- [x] Data augmentation applied
- [x] Best model saved automatically
- [ ] Run quick_train_mastitis.py
- [ ] Test results in app.py
- [ ] (Optional) Run full training for production

**Next Step:** 
```bash
python quick_train_mastitis.py    # Start training
```

After it completes, restart `app.py` and test Mastitis detection with cow images! 🐄✨
