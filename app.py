"""
🌐 Skin Disease Detection System — Flask Web Application
"""

import hashlib
import json
import os
import sqlite3
import traceback
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (Flask, jsonify, redirect, render_template,
                   request, send_from_directory, session, url_for)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SKIN_APP_SECRET", "skin-disease-secret-2026-change-me")

# ── Config ─────────────────────────────────────────────────────────────────────
UPLOAD_FOLDER      = Path("uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp"}
MAX_FILE_SIZE      = 10 * 1024 * 1024   # 10 MB
MODEL_PATH         = Path(os.environ.get("SKIN_DISEASE_MODEL", "models/best_model.pt"))

UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"]       = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"]  = MAX_FILE_SIZE

# ── Lazy-load predictor ────────────────────────────────────────────────────────
_predictor = None

def get_predictor():
    global _predictor
    if _predictor is not None:
        return _predictor
    if not MODEL_PATH.exists():
        return None
    try:
        from detection import SkinDiseasePredictor
        _predictor = SkinDiseasePredictor(model_path=MODEL_PATH)
        print(f"✅ Model loaded — {len(_predictor.classes)} classes: {_predictor.classes}")
    except Exception as exc:
        print(f"⚠️  Could not load model: {exc}")
    return _predictor


# ── Database ───────────────────────────────────────────────────────────────────
class Database:
    PATH = "skin_disease.db"

    def conn(self):
        c = sqlite3.connect(self.PATH)
        c.row_factory = sqlite3.Row
        return c

    def init(self):
        with self.conn() as cx:
            cx.executescript("""
                CREATE TABLE IF NOT EXISTS patients (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    name         TEXT    NOT NULL,
                    email        TEXT    UNIQUE NOT NULL,
                    password     TEXT    NOT NULL,
                    age          INTEGER,
                    gender       TEXT,
                    phone        TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS diseases (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL,
                    description TEXT,
                    symptoms    TEXT,
                    treatment   TEXT,
                    prevention  TEXT
                );
                CREATE TABLE IF NOT EXISTS diagnoses (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id     INTEGER,
                    disease_name   TEXT,
                    confidence     REAL,
                    top_results    TEXT,
                    image_path     TEXT,
                    diagnosis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id)
                );
            """)
            if cx.execute("SELECT COUNT(*) FROM diseases").fetchone()[0] == 0:
                cx.executemany(
                    "INSERT INTO diseases (name,description,symptoms,treatment,prevention)"
                    " VALUES (?,?,?,?,?)",
                    [
                        ("Melanoma",            "Serious skin cancer",
                         "Changing mole, Irregular borders, Multiple colours",
                         "Surgical excision, Immunotherapy, Targeted therapy",
                         "Use sunscreen SPF 30+, Avoid tanning beds, Regular skin checks"),
                        ("Melanocytic_Nevi",    "Common benign mole",
                         "Round, Uniform colour, Smooth border",
                         "Monitoring, Excision if changes noted",
                         "Regular dermatologist review"),
                        ("Basal_Cell_Carcinoma","Most common skin cancer",
                         "Pearly bump, Pink growth, Flat flesh-coloured lesion",
                         "Surgical removal, Mohs surgery, Radiation",
                         "Limit UV exposure, Wear protective clothing"),
                        ("Actinic_Keratosis",   "Pre-cancerous rough patch",
                         "Rough scaly patch, Dry skin, Colour variation",
                         "Cryotherapy, Topical fluorouracil, Photodynamic therapy",
                         "Sunscreen, Protective clothing, Avoid peak sun hours"),
                        ("Benign_Keratosis",    "Non-cancerous skin growth",
                         "Waxy raised lesion, Brown or black colour",
                         "Usually none required; cryotherapy if bothersome",
                         "No specific prevention"),
                        ("Dermatofibroma",      "Benign fibrous skin nodule",
                         "Firm bump, Brown-pink colour, Dimples on pinching",
                         "Usually none; surgical removal if symptomatic",
                         "No specific prevention"),
                        ("Vascular_Lesion",     "Blood vessel skin abnormality",
                         "Red/purple discolouration, May bleed on trauma",
                         "Laser therapy, Sclerotherapy",
                         "Protect skin from trauma"),
                    ]
                )

    def register(self, name, email, password, age=None, gender=None, phone=None):
        pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            with self.conn() as cx:
                cx.execute(
                    "INSERT INTO patients (name,email,password,age,gender,phone)"
                    " VALUES (?,?,?,?,?,?)",
                    (name, email, pw, age, gender, phone),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def login(self, email, password):
        pw  = hashlib.sha256(password.encode()).hexdigest()
        row = self.conn().execute(
            "SELECT id,name,email,age,gender,phone FROM patients"
            " WHERE email=? AND password=?", (email, pw)
        ).fetchone()
        return dict(row) if row else None

    def save_diagnosis(self, patient_id, disease_name, confidence, top_results, image_path):
        with self.conn() as cx:
            cur = cx.execute(
                "INSERT INTO diagnoses"
                " (patient_id,disease_name,confidence,top_results,image_path)"
                " VALUES (?,?,?,?,?)",
                (patient_id, disease_name, confidence,
                 json.dumps(top_results), str(image_path)),
            )
            return cur.lastrowid

    def get_history(self, patient_id, limit=50):
        rows = self.conn().execute(
            "SELECT id,disease_name,confidence,top_results,image_path,diagnosis_date"
            " FROM diagnoses WHERE patient_id=?"
            " ORDER BY diagnosis_date DESC LIMIT ?",
            (patient_id, limit),
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try:
                d["top_results"] = json.loads(d["top_results"] or "[]")
            except Exception:
                d["top_results"] = []
            result.append(d)
        return result

    def stats(self):
        cx = self.conn()
        return {
            "patients":  cx.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
            "diagnoses": cx.execute("SELECT COUNT(*) FROM diagnoses").fetchone()[0],
        }


db = Database()


# ── Helpers ────────────────────────────────────────────────────────────────────
def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def wrap(*a, **kw):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrap


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = db.login(request.form["email"], request.form["password"])
        if user:
            session["user"] = user
            return redirect(url_for("dashboard"))
        error = "Invalid email or password."
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        ok = db.register(
            request.form["name"], request.form["email"], request.form["password"],
            request.form.get("age"), request.form.get("gender"), request.form.get("phone"),
        )
        if ok:
            return redirect(url_for("login"))
        error = "Email already registered."
    return render_template("register.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    history     = db.get_history(session["user"]["id"], limit=5)
    model_ready = get_predictor() is not None
    s           = db.stats()
    # Fetch diseases list for the dashboard
    with db.conn() as cx:
        diseases = [dict(r) for r in cx.execute("SELECT * FROM diseases").fetchall()]
    stats = {
        "patients":  s["patients"],
        "diagnoses": s["diagnoses"],
        "diseases":  len(diseases),
    }
    return render_template("dashboard.html", user=session["user"],
                           history=history, model_ready=model_ready,
                           stats=stats, diseases=diseases)


@app.route("/detect", methods=["GET", "POST"])
@login_required
def detect():
    predictor   = get_predictor()
    model_ready = predictor is not None

    if request.method == "POST":
        if not model_ready:
            return jsonify({"error": "Model not loaded. Run train.py first."}), 503

        file = request.files.get("image")
        if not file or not allowed(file.filename):
            return jsonify({"error": "Invalid or missing image file (JPG/PNG/BMP)."}), 400

        fname    = secure_filename(file.filename)
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S_")
        save_path = UPLOAD_FOLDER / (ts + fname)
        file.save(save_path)

        try:
            results           = predictor.predict(save_path, top_k=3)
            top_name, top_conf = results[0]
            db.save_diagnosis(session["user"]["id"], top_name, top_conf,
                              results, save_path)
            return jsonify({
                "success":         True,
                "top_prediction":  top_name,
                "confidence":      top_conf,
                "all_predictions": [{"name": n, "confidence": c} for n, c in results],
                "image_url":       f"/uploads/{save_path.name}",
            })
        except Exception as exc:
            traceback.print_exc()
            return jsonify({"error": str(exc)}), 500

    return render_template("detection.html", user=session["user"], model_ready=model_ready)


@app.route("/history")
@login_required
def history():
    records = db.get_history(session["user"]["id"])
    return render_template("history.html", user=session["user"], records=records)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=session["user"])


@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/api/status")
def api_status():
    p = get_predictor()
    return jsonify({
        "model_loaded": p is not None,
        "classes":      p.classes if p else [],
        "model_path":   str(MODEL_PATH),
    })


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    db.init()
    print("🌐 Skin Disease Detection Web App")
    print(f"   Model: {MODEL_PATH}")
    if not MODEL_PATH.exists():
        print("   ⚠️  Model not found — train the model first, then restart.")
    print("   Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
