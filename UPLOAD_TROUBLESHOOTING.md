# 🔧 Image Upload Troubleshooting Guide

## Quick Diagnosis Steps

### Step 1: Verify Server is Running
```bash
# Check if Flask server is running
# Terminal output should show:
# * Running on http://127.0.0.1:5000

# If not running, start it:
python app.py
```

### Step 2: Check Browser Console for Errors
1. Open app in browser: `http://localhost:5000/`
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Try uploading image
5. Look for error messages in console
6. Share any `[UPLOAD]` or `[ERROR]` messages

### Step 3: Check Server Terminal Output
When you upload an image, the Python terminal should show:
```
[DEBUG] Upload request received
[DEBUG] Request files: dict_keys(['image'])
[DEBUG] Image filename: photo.jpg
[DEBUG] Image saved to: uploads/photo.jpg
[DEBUG] Starting preprocessing...
[DEBUG] Image preprocessed successfully
[DEBUG] Starting disease detection...
[DEBUG] Diagnosis result: Mastitis
[DEBUG] Returning diagnosis response
```

---

## Common Issues & Solutions

### ❌ "Cannot connect to server"
**Symptoms:** 
- Browser shows: "Cannot connect to server"
- Console shows: Failed to fetch

**Solutions:**
1. Ensure Python app.py is running in terminal
2. Check URL is: `http://127.0.0.1:5000` or `http://localhost:5000`
3. Verify port 5000 is not blocked
4. Try accessing homepage first to test connection
5. Restart Flask server:
   ```bash
   python app.py
   ```

---

### ❌ "No image file uploaded"
**Symptoms:**
- Click upload, nothing happens
- No error message appears

**Solutions:**
1. Check if image file is selected (preview should show)
2. Try different image formats: JPG, PNG, GIF
3. Ensure image file size is reasonable (< 50MB)
4. Check browser DevTools Console for errors (F12)
5. Try different browser (Chrome, Firefox, Safari)

---

### ❌ "Server returned invalid response"
**Symptoms:**
- Error: "Server returned invalid response"
- Console shows garbled text

**Solutions:**
1. Check Python terminal for error messages
2. Verify image file is valid (not corrupted)
3. Check `uploads/` folder exists: `ls uploads/` or `dir uploads`
4. Check model file exists: `ls Models/` or `dir Models`
5. Restart Python server with full error output:
   ```bash
   python -u app.py 2>&1
   ```

---

### ❌ "Image processing failed"
**Symptoms:**
- Error: "Could not read image file"
- Server shows: [ERROR] Image preprocessing failed

**Solutions:**
1. Try a different image file
2. Ensure image format is supported (JPG, PNG)
3. Open image in viewer to confirm it's valid
4. Check file extension matches content (e.g., not .txt named as .jpg)
5. Verify image_preprocessing.py is working:
   ```bash
   python -c "from processing.image_preprocessing import preprocess_image; print('OK')"
   ```

---

### ❌ "Model not found" error
**Symptoms:**
- Server shows: [ERROR] Model file not found
- Error mentions `livestock_disease_detection.pth`

**Solutions:**
1. Check model file exists: `Models/livestock_disease_detection.pth`
2. If missing, train model or download it
3. Verify file permissions (readable)
4. Check file size > 100MB
5. Restart server after model is available

---

## Testing the Upload Flow

### Manual Test with curl (if on Windows with curl):
```bash
# Test with a sample image
curl -F "image=@test_image.jpg" http://127.0.0.1:5000/upload
```

### Browser Console Test:
```javascript
// Open Console (F12) and run:
const input = document.getElementById('imageInput');
console.log('Image input element:', input);
console.log('Selected file:', input.files[0]);
```

---

## Debug Checklist

When uploading, verify ALL of these are true:

- ✅ Flask server is running (terminal shows `Running on http://127.0.0.1:5000`)
- ✅ Image file is selected (preview shows image)
- ✅ Image format is supported (JPG, PNG, GIF)
- ✅ Image file size is reasonable (< 50MB)
- ✅ `uploads/` folder exists
- ✅ `Models/livestock_disease_detection.pth` exists
- ✅ PyTorch is installed
- ✅ Browser allows file uploads (no JavaScript errors in console)
- ✅ Network connection is working
- ✅ No firewall blocking port 5000

---

## Enable Maximum Debugging

### In Python terminal:
```bash
# Run with debug output:
python -u app.py 2>&1 | tee debug.log

# This shows all output in realtime AND saves to debug.log
```

### In Browser console:
```javascript
// Monitor network requests
// Open DevTools → Network tab
// Try uploading
// Look for POST request to /upload
// Click it to see request/response details
```

---

## Check Flask Configuration

```bash
# In Python terminal, verify setup:
python -c "
from app import app
print('UPLOAD_FOLDER:', app.config['UPLOAD_FOLDER'])
print('App debug:', app.debug)
print('Secret key set:', bool(app.secret_key))
print('Models folder exists:', __import__('os').path.exists('Models'))
print('Uploads folder exists:', __import__('os').path.exists('uploads'))
"
```

---

## Network Troubleshooting

### Check if port 5000 is accessible:
```bash
# Windows PowerShell:
Test-NetConnection -ComputerName 127.0.0.1 -Port 5000

# Or try in browser:
# Open: http://127.0.0.1:5000/
# Should see your app, not "Connection Refused"
```

---

## Step-by-Step Verification

1. **Server Running?**
   ```bash
   # Terminal shows this:
   # * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
   ```

2. **Uploads Folder Ready?**
   ```bash
   ls -la uploads/
   # or on Windows:
   dir uploads
   ```

3. **Model Ready?**
   ```bash
   ls -la Models/livestock_disease_detection.pth
   # Should show file > 100MB
   ```

4. **Image Valid?**
   - Open image in photo viewer
   - Confirm it displays correctly
   - Check file size < 50MB

5. **Browser Working?**
   - Open DevTools (F12)
   - Go to Console tab
   - Should be empty (no red errors)

---

## Still Having Issues?

1. **Capture Full Error Output:**
   ```bash
   # Run this and try upload, capture output:
   python -u app.py 2>&1
   ```

2. **Check Browser Console:**
   - Right-click page → Inspect
   - Click Console tab
   - Copy any error messages

3. **Enable Verbose Logging:**
   Edit `app.py`, find `@app.route("/upload"...)` and add:
   ```python
   print(f"[DEBUG] Headers: {dict(request.headers)}")
   print(f"[DEBUG] Form data: {dict(request.form)}")
   ```

4. **Test with Different Image:**
   - Try JPG, PNG, different file
   - Try smaller/larger image
   - Try compressed vs uncompressed

---

## Advanced: Check Model Loading

```bash
python -c "
import torch
from processing.disease_detection import load_model

try:
    model = load_model(num_classes=4, weights_path='Models/livestock_disease_detection.pth', model_name='resnet50')
    print('[OK] Model loaded successfully')
    print('Model:', model)
except Exception as e:
    print('[ERROR] Failed to load model:', e)
    import traceback
    traceback.print_exc()
"
```

---

## Contact Support

If still stuck, provide:
1. Full Python terminal output
2. Browser console error messages
3. Network tab details from DevTools
4. File listing of `Models/` and `uploads/` folders
5. Python version: `python --version`

---

**Status Check Command:**
```bash
# Quick status check:
python -c "
import os
print('Python OK')
import torch
print('PyTorch OK')
print('Uploads folder:', os.path.exists('uploads/'))
print('Models folder:', os.path.exists('Models/'))
print('Model file:', os.path.exists('Models/livestock_disease_detection.pth'))
"
```

Run this to quickly verify all dependencies are installed and paths are correct!
