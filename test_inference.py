from processing.image_preprocessing import preprocess_image
import app

img_path = 'uploads/footrot.jpg'
print('Using model loaded in app...')
img = preprocess_image(img_path)
if img is None:
    print('Image preprocessing failed')
else:
    res = app.detect_disease(img, app.model, app.class_names) if hasattr(app, 'detect_disease') else None
    # If detect_disease not exposed on app, import from processing
    if res is None:
        from processing.disease_detection import detect_disease
        res = detect_disease(img, app.model, app.class_names)
    print('RESULT:')
    print(res)
