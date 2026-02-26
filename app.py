from flask import Flask, request, jsonify, render_template, send_from_directory, url_for, session, redirect
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import time
import json
from processing.disease_detection import detect_disease, load_model
from processing.image_preprocessing import preprocess_image
import torch

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("APP_SECRET_KEY", "change-me-please")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # limit uploads to 16MB

# Allowed image extensions for uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp"}
os.makedirs("Models", exist_ok=True)

# --- Load pretrained livestock disease detection model ---
# Default class names (fallback)
default_class_names = [
    "Healthy",
    "Lumpy Skin Disease",
    "Foot Rot",
    "Mastitis",
    "Blackleg",
    "Anthrax Disease",
    "Tick-Borne Fever"
]

# If a checkpoint exists, prefer the class ordering saved with it
weights_path = "Models/livestock_disease_detection.pth"
if os.path.exists(weights_path):
    try:
        print("[INFO] Checking checkpoint metadata...")
        ckpt = torch.load(weights_path, map_location="cpu")
        ckpt_class_names = ckpt.get("class_names") if isinstance(ckpt, dict) else None
        ckpt_num_classes = ckpt.get("num_classes") if isinstance(ckpt, dict) else None
        if ckpt_class_names and isinstance(ckpt_class_names, (list, tuple)) and len(ckpt_class_names) > 0:
            class_names = list(ckpt_class_names)
            print(f"[INFO] Loaded class_names from checkpoint: {class_names}")
        else:
            class_names = default_class_names
            print("[INFO] No class_names found in checkpoint; using default class list")
        num_classes = int(ckpt_num_classes) if ckpt_num_classes else len(class_names)
    except Exception as e:
        print(f"[WARN] Could not read checkpoint metadata: {e}")
        class_names = default_class_names
        num_classes = len(class_names)
else:
    class_names = default_class_names
    num_classes = len(class_names)

# Initialize model as None - will load on first upload
model = None

def ensure_model_loaded():
    """Load model lazily on first use to speed up server startup"""
    global model
    if model is None:
        print("[INFO] Loading model (lazy load)...")
        model = load_model(num_classes=num_classes, weights_path=weights_path, model_name="resnet50")
        print("[OK] Model loaded and ready")
    return model

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    """Mobile-friendly dashboard with analytics"""
    return render_template("dashboard.html")

@app.route("/test-upload")
def test_upload_page():
    """Diagnostic upload test page"""
    return render_template("upload_test.html")

@app.route("/upload-test-simple", methods=["POST"])
def upload_test_simple():
    """Simplified upload endpoint for testing (no model processing)"""
    print("[DEBUG-SIMPLE] Simple upload test received")
    
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    image = request.files["image"]
    
    if image.filename == "":
        return jsonify({"error": "No selected image"}), 400
    
    print(f"[DEBUG-SIMPLE] Got file: {image.filename} ({image.content_length} bytes)")
    
    return jsonify({
        "Diagnosis": "Test - Healthy",
        "Confidence": "95.00%",
        "Status": "✓ Test Mode",
        "Severity": "None",
        "Action": "This is a test response",
        "Treatment": "N/A",
        "Contagious": "No",
        "Quarantine": "N/A"
    })

@app.route("/upload", methods=["POST"])
def upload_image():
    print("[DEBUG] Upload request received")
    print(f"[DEBUG] Request files: {request.files.keys()}")
    print(f"[DEBUG] Request form: {request.form.keys()}")
    
    if "image" not in request.files:
        print("[ERROR] No 'image' key in request.files")
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    print(f"[DEBUG] Image filename: {image.filename}")
    
    if image.filename == "":
        print("[ERROR] Empty filename")
        return jsonify({"error": "No selected image"}), 400

    # Get optional behavior description from farmer
    behavior_description = request.form.get("behavior_description", "").strip()
    print(f"[DEBUG] Behavior description present: {bool(behavior_description)}")

    # Validate extension and save file safely
    try:
        filename = image.filename
        if "." not in filename:
            return jsonify({"error": "Uploaded file has no extension"}), 400
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": f"Unsupported image format: .{ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"}), 400

        safe_name = f"{int(time.time())}_{secure_filename(filename)}"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
        image.save(image_path)
        print(f"[DEBUG] Image saved to: {image_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save image: {e}")
        return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

    try:
        # 1. Ensure model is loaded
        print(f"[DEBUG] Ensuring model is loaded...")
        current_model = ensure_model_loaded()
        
        # 2. Preprocess
        print(f"[DEBUG] Starting preprocessing...")
        processed_image = preprocess_image(image_path)
        
        if processed_image is None:
            print("[ERROR] Image preprocessing failed")
            return jsonify({
                "error": "Image processing failed",
                "details": f"Could not read image file: {image.filename}. Ensure it's a valid image format (JPG, PNG, etc.)"
            }), 400
        
        print(f"[DEBUG] Image preprocessed successfully")
        
        # 3. Detect (now with model + class_names)
        print(f"[DEBUG] Starting disease detection...")
        diagnosis = detect_disease(processed_image, current_model, class_names)
        print(f"[DEBUG] Diagnosis result: {diagnosis.get('Diagnosis', 'Unknown')}")
        
        # 4. Enhance diagnosis with behavior context if provided
        if behavior_description:
            diagnosis["farmer_notes"] = behavior_description
            diagnosis["analysis_enhanced"] = True
            print(f"[INFO] Enhanced diagnosis with farmer's behavior notes")

        # 5. Add timestamp for dashboard tracking
        diagnosis["timestamp"] = int(time.time() * 1000)  # milliseconds for JS
        diagnosis["image_filename"] = safe_name
        try:
            diagnosis["image_url"] = url_for('uploaded_file', filename=safe_name, _external=True)
        except Exception:
            diagnosis["image_url"] = None

        # 6. Optional delay for frontend spinner
        time.sleep(1)

        print(f"[DEBUG] Returning diagnosis response")
        return jsonify(diagnosis)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Processing failed", "details": str(e)}), 500


@app.route('/report', methods=['POST'])
def report_case():
    try:
        reports_dir = 'reports'
        os.makedirs(reports_dir, exist_ok=True)

        # Collect metadata from form
        metadata = {}
        for k in request.form:
            metadata[k] = request.form.get(k)

        # Extract and document behavior description if provided
        behavior_description = metadata.get('behavior_description', '').strip()
        if behavior_description:
            metadata['behavior_description'] = behavior_description
            metadata['includes_farmer_notes'] = True
            print(f"[REPORT] Case includes farmer behavioral notes")
        else:
            metadata['includes_farmer_notes'] = False

        timestamp = int(time.time())
        image_saved = None
        if 'image' in request.files and request.files['image'].filename != '':
            img = request.files['image']
            safe_name = f"{timestamp}_{secure_filename(img.filename)}"
            save_path = os.path.join(reports_dir, safe_name)
            img.save(save_path)
            image_saved = save_path

        metadata['image_saved'] = image_saved
        metadata['reported_at'] = timestamp
        
        # Add report metadata
        metadata['report_id'] = timestamp
        metadata['includes_image'] = bool(image_saved)

        meta_path = os.path.join(reports_dir, f"{timestamp}_meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        print(f"[REPORT] Case saved to {meta_path}")
        return jsonify({"ok": True, "message": "Report saved with farmer notes", "meta": meta_path})
    except Exception as e:
        print(f"Report failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "message": str(e)}), 500


@app.route('/reports')
def list_reports():
    # Require admin session
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login', next=request.path))

    reports_dir = 'reports'
    os.makedirs(reports_dir, exist_ok=True)

    metas = []
    for fname in sorted(os.listdir(reports_dir), reverse=True):
        if fname.endswith('_meta.json'):
            try:
                with open(os.path.join(reports_dir, fname), 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    img_path = meta.get('image_saved')
                    if img_path:
                        img_name = os.path.basename(img_path)
                        meta['image_url'] = url_for('report_file', filename=img_name)
                    else:
                        meta['image_url'] = None
                    metas.append(meta)
            except Exception:
                continue

    # Pagination
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    per_page = 6
    total = len(metas)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    page_items = metas[start:end]

    prev_url = url_for('list_reports', page=page - 1) if page > 1 else None
    next_url = url_for('list_reports', page=page + 1) if page < total_pages else None

    return render_template('reports.html', reports=page_items, page=page, total_pages=total_pages, prev_url=prev_url, next_url=next_url)


@app.route('/reports/files/<path:filename>')
def report_file(filename):
    return send_from_directory('reports', filename)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded images from the uploads folder."""
    return send_from_directory(app.config.get("UPLOAD_FOLDER", "uploads"), filename)


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    # Simple password-protected login for admin reports page
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        # Prefer a hashed password in environment for stronger verification
        expected_hash = os.environ.get('REPORTS_ADMIN_PASSWORD_HASH')
        fallback_plain = os.environ.get('REPORTS_ADMIN_PASSWORD', 'adminpass')

        valid = False
        if expected_hash:
            try:
                valid = check_password_hash(expected_hash, pwd)
            except Exception:
                valid = False
        else:
            # No hash provided — fallback to plaintext comparison (less secure)
            valid = (pwd == fallback_plain)

        if valid:
            session['admin_logged_in'] = True
            next_url = request.args.get('next') or url_for('list_reports')
            return redirect(next_url)
        else:
            return render_template('admin_login.html', error='Invalid password')

    return render_template('admin_login.html')


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get PORT from Render, default to 5000 locally
    app.run(host="0.0.0.0", port=port)        # Bind to all interfaces