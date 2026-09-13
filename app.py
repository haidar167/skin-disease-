"""
🌐 SKIN DISEASE DETECTION SYSTEM - WEB VERSION
Web application using Flask for browser-based access
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import hashlib
import os
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'skin-disease-secret-key-2026'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ==================== DATABASE ====================
class Database:
    def __init__(self):
        self.db_path = 'skin_disease.db'
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables if not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                phone TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                symptoms TEXT,
                treatment TEXT,
                prevention TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                disease_id INTEGER,
                confidence REAL,
                image_path TEXT,
                diagnosis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (disease_id) REFERENCES diseases(id)
            )
        ''')
        
        conn.commit()
        
        # Insert default diseases if not exist
        cursor.execute('SELECT COUNT(*) FROM diseases')
        if cursor.fetchone()[0] == 0:
            diseases = [
                ('Acne', 'Common skin condition with pimples',
                 'Whiteheads, Blackheads, Pimples, Cysts',
                 'Benzoyl Peroxide, Retinoids, Antibiotics',
                 'Clean skin regularly, Avoid touching face'),
                
                ('Eczema', 'Itchy, inflamed skin condition',
                 'Itchy skin, Redness, Dry patches, Inflammation',
                 'Moisturizers, Corticosteroid creams',
                 'Moisturize daily, Avoid triggers'),
                
                ('Psoriasis', 'Autoimmune condition causing skin cell buildup',
                 'Red patches, Silvery scales, Dry skin, Itching',
                 'Topical treatments, Light therapy',
                 'Avoid triggers, Reduce stress'),
                
                ('Ringworm', 'Fungal skin infection',
                 'Circular rash, Itchy, Red, Scaly',
                 'Antifungal creams, Oral antifungals',
                 'Keep skin dry, Avoid sharing items'),
                
                ('Melanoma', 'Serious type of skin cancer',
                 'Changing mole, Irregular borders, Multiple colors',
                 'Surgical excision, Immunotherapy',
                 'Sun protection, Regular skin checks')
            ]
            
            for disease in diseases:
                cursor.execute('''
                    INSERT INTO diseases (name, description, symptoms, treatment, prevention)
                    VALUES (?, ?, ?, ?, ?)
                ''', disease)
            
            conn.commit()
        
        conn.close()
    
    def register_patient(self, name, email, password, age, gender, phone):
        """Register new patient"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO patients (name, email, password, age, gender, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, hashed_password, age, gender, phone))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def login_patient(self, email, password):
        """Login patient"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, age, gender, phone FROM patients
            WHERE email=? AND password=?
        ''', (email, hashed_password))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def get_all_diseases(self):
        """Get all diseases"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM diseases')
        diseases = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return diseases
    
    def get_disease_by_id(self, disease_id):
        """Get disease by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM diseases WHERE id=?', (disease_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def save_diagnosis(self, patient_id, disease_id, confidence, image_path):
        """Save diagnosis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnoses (patient_id, disease_id, confidence, image_path)
            VALUES (?, ?, ?, ?)
        ''', (patient_id, disease_id, confidence, image_path))
        conn.commit()
        diagnosis_id = cursor.lastrowid
        conn.close()
        return diagnosis_id
    
    def get_patient_diagnoses(self, patient_id):
        """Get all diagnoses for a patient"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.id, dis.name, d.confidence, d.diagnosis_date, d.image_path
            FROM diagnoses d
            JOIN diseases dis ON d.disease_id = dis.id
            WHERE d.patient_id = ?
            ORDER BY d.diagnosis_date DESC
        ''', (patient_id,))
        diagnoses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return diagnoses
    
    def get_system_stats(self):
        """Get system statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM patients')
        patients = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM diseases')
        diseases = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM diagnoses')
        diagnoses = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'patients': patients,
            'diseases': diseases,
            'diagnoses': diagnoses
        }

db = Database()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = db.login_patient(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        
        if db.register_patient(name, email, password, age, gender, phone):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Registration failed. Email may already exist.')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Patient dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    stats = db.get_system_stats()
    diseases = db.get_all_diseases()
    
    return render_template('dashboard.html', 
                         user_name=session['user_name'],
                         user_email=session['user_email'],
                         stats=stats,
                         diseases=diseases)

@app.route('/detection')
def detection():
    """Disease detection page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('detection.html',
                         user_name=session['user_name'])

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded image"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], timestamp + filename)
    file.save(filepath)
    
    # Mock prediction (in real app, use trained model)
    diseases = db.get_all_diseases()
    predicted_disease = diseases[0]  # Default to first disease
    confidence = 78.5
    
    # Save diagnosis
    diagnosis_id = db.save_diagnosis(
        session['user_id'],
        predicted_disease['id'],
        confidence,
        filepath
    )
    
    return jsonify({
        'success': True,
        'diagnosis_id': diagnosis_id,
        'disease': predicted_disease['name'],
        'confidence': confidence,
        'description': predicted_disease['description'],
        'symptoms': predicted_disease['symptoms'],
        'treatment': predicted_disease['treatment'],
        'prevention': predicted_disease['prevention']
    })

@app.route('/history')
def history():
    """Diagnosis history page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    diagnoses = db.get_patient_diagnoses(session['user_id'])
    
    return render_template('history.html',
                         user_name=session['user_name'],
                         diagnoses=diagnoses)

@app.route('/profile')
def profile():
    """Patient profile page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('profile.html',
                         user_id=session['user_id'],
                         user_name=session['user_name'],
                         user_email=session['user_email'])

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    stats = db.get_system_stats()
    return jsonify(stats)

def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
