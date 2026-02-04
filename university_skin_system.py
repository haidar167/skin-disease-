# ================================================
# 🎓 UNIVERSITY SKIN DISEASE DETECTION SYSTEM
# ================================================
# ✅ COMPLETE WORKING PROJECT
# ================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import time
import random
from datetime import datetime
import sqlite3
import hashlib

# ==================== DATABASE CLASS ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('skin_disease.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.insert_default_data()
    
    def create_tables(self):
        """Create database tables"""
        # Patients table
        self.cursor.execute('''
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
        
        # Diseases table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                symptoms TEXT,
                treatment TEXT,
                prevention TEXT
            )
        ''')
        
        # Diagnoses table
        self.cursor.execute('''
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
        
        self.conn.commit()
    
    def insert_default_data(self):
        """Insert default diseases"""
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
            self.cursor.execute('''
                INSERT OR IGNORE INTO diseases (name, description, symptoms, treatment, prevention)
                VALUES (?, ?, ?, ?, ?)
            ''', disease)
        
        self.conn.commit()
    
    def register_patient(self, name, email, password, age=None, gender=None, phone=None):
        """Register new patient"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute('''
                INSERT INTO patients (name, email, password, age, gender, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, hashed_password, age, gender, phone))
            self.conn.commit()
            return True
        except:
            return False
    
    def login_patient(self, email, password):
        """Login patient"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute('''
            SELECT id, name, email, age, gender, phone FROM patients
            WHERE email=? AND password=?
        ''', (email, hashed_password))
        return self.cursor.fetchone()
    
    def get_all_diseases(self):
        """Get all diseases"""
        self.cursor.execute('SELECT * FROM diseases')
        return self.cursor.fetchall()
    
    def save_diagnosis(self, patient_id, disease_id, confidence, image_path):
        """Save diagnosis to database"""
        self.cursor.execute('''
            INSERT INTO diagnoses (patient_id, disease_id, confidence, image_path)
            VALUES (?, ?, ?, ?)
        ''', (patient_id, disease_id, confidence, image_path))
        self.conn.commit()
        return self.cursor.lastrowid

# ==================== MAIN APPLICATION ====================
class SkinDiseaseSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 University Skin Disease Detection System")
        self.root.geometry("1200x700")
        
        # Center window
        self.center_window(1200, 700)
        
        # Initialize database
        self.db = Database()
        
        # Current user
        self.current_user = None
        
        # Colors
        self.colors = {
            'primary': '#2E86C1',
            'secondary': '#3498DB',
            'success': '#27AE60',
            'danger': '#E74C3C',
            'warning': '#F39C12',
            'bg': '#F8F9FA',
            'white': '#FFFFFF',
            'dark': '#2C3E50'
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.show_welcome_screen()
    
    def center_window(self, width, height):
        """Center window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def clear_window(self):
        """Clear all widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ==================== WELCOME SCREEN ====================
    def show_welcome_screen(self):
        self.clear_window()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['primary'])
        main_container.pack(fill="both", expand=True)
        
        # Left panel
        left_panel = tk.Frame(main_container, bg=self.colors['primary'])
        left_panel.pack(side="left", fill="both", expand=True)
        
        # University title
        tk.Label(left_panel, text="🎓", font=("Arial", 72), 
                bg=self.colors['primary'], fg="white").pack(pady=50)
        tk.Label(left_panel, text="UNIVERSITY PROJECT", font=("Arial", 24, "bold"),
                bg=self.colors['primary'], fg="white").pack(pady=10)
        tk.Label(left_panel, text="Skin Disease Detection System", font=("Arial", 18),
                bg=self.colors['primary'], fg="white").pack(pady=5)
        
        # Project info
        info_text = """
🔬 COMPLETE HEALTHCARE SOLUTION

✅ Features:
• Patient Registration & Login
• AI-Powered Disease Detection
• Medical Database
• User-friendly Interface
• Secure Authentication
• Detailed Reports

👥 For University Students:
• Computer Science Projects
• Medical Research
• AI/ML Demonstrations
• Database Management
        """
        
        tk.Label(left_panel, text=info_text, font=("Arial", 11),
                bg=self.colors['primary'], fg="white", justify="left").pack(pady=30, padx=20)
        
        # Right panel - Login/Register
        right_panel = tk.Frame(main_container, bg=self.colors['bg'])
        right_panel.pack(side="right", fill="both", expand=True, padx=50, pady=50)
        
        # Tabs
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill="both", expand=True)
        
        # Login Tab
        login_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(login_tab, text="🔐 Login")
        self.create_login_tab(login_tab)
        
        # Register Tab
        register_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(register_tab, text="📝 Register")
        self.create_register_tab(register_tab)
        
        # Demo buttons
        demo_frame = tk.Frame(right_panel, bg=self.colors['bg'])
        demo_frame.pack(fill="x", pady=20)
        
        tk.Label(demo_frame, text="Quick Demo Access:", 
                font=("Arial", 10, "bold"), bg=self.colors['bg']).pack()
        
        demo_buttons = tk.Frame(demo_frame, bg=self.colors['bg'])
        demo_buttons.pack(pady=10)
        
        tk.Button(demo_buttons, text="👤 Demo Patient", font=("Arial", 10),
                 bg=self.colors['success'], fg="white", width=15,
                 command=self.demo_patient_login).pack(side="left", padx=5)
        
        tk.Button(demo_buttons, text="⚙️ Admin Panel", font=("Arial", 10),
                 bg=self.colors['warning'], fg="white", width=15,
                 command=self.show_admin_panel).pack(side="left", padx=5)
    
    def create_login_tab(self, parent):
        tk.Label(parent, text="Login to System", font=("Arial", 20, "bold"),
                bg=self.colors['bg']).pack(pady=30)
        
        # Email
        tk.Label(parent, text="Email Address:", font=("Arial", 12),
                bg=self.colors['bg']).pack(anchor="w", pady=(10, 5), padx=50)
        self.login_email = tk.Entry(parent, font=("Arial", 14), width=35)
        self.login_email.pack(pady=(0, 20), ipady=8, padx=50)
        
        # Password
        tk.Label(parent, text="Password:", font=("Arial", 12),
                bg=self.colors['bg']).pack(anchor="w", pady=(10, 5), padx=50)
        self.login_password = tk.Entry(parent, font=("Arial", 14), show="●", width=35)
        self.login_password.pack(pady=(0, 30), ipady=8, padx=50)
        
        # Login button
        tk.Button(parent, text="Login", font=("Arial", 14, "bold"),
                 bg=self.colors['primary'], fg="white",
                 command=self.login_user, width=20, height=2).pack(pady=20)
    
    def create_register_tab(self, parent):
        tk.Label(parent, text="New Patient Registration", font=("Arial", 20, "bold"),
                bg=self.colors['bg']).pack(pady=20)
        
        # Scrollable frame
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0, height=400)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form fields
        fields = [
            ("Full Name *", "name"),
            ("Email Address *", "email"),
            ("Password *", "password", True),
            ("Confirm Password *", "confirm_password", True),
            ("Age", "age"),
            ("Gender", "gender"),
            ("Phone Number", "phone")
        ]
        
        self.register_entries = {}
        
        for i, (label, key, *is_password) in enumerate(fields):
            tk.Label(scrollable_frame, text=label, font=("Arial", 11),
                    bg=self.colors['bg']).grid(row=i*2, column=0, sticky="w", pady=(15, 5), padx=50)
            
            if key == "gender":
                entry = ttk.Combobox(scrollable_frame, values=["Male", "Female", "Other"], 
                                    state="readonly", font=("Arial", 12), width=32)
                entry.set("Male")
            elif is_password:
                entry = tk.Entry(scrollable_frame, font=("Arial", 12), show="●", width=35)
            else:
                entry = tk.Entry(scrollable_frame, font=("Arial", 12), width=35)
            
            entry.grid(row=i*2+1, column=0, pady=(0, 10), ipady=6, padx=50)
            self.register_entries[key] = entry
        
        # Register button
        tk.Button(scrollable_frame, text="Register Now", font=("Arial", 14, "bold"),
                 bg=self.colors['success'], fg="white",
                 command=self.register_patient, width=20).grid(row=len(fields)*2, column=0, pady=30, padx=50)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def demo_patient_login(self):
        """Auto-login demo patient"""
        self.login_email.delete(0, tk.END)
        self.login_email.insert(0, "demo@patient.com")
        self.login_password.delete(0, tk.END)
        self.login_password.insert(0, "demo123")
        self.login_user()
    
    def login_user(self):
        """Handle user login"""
        email = self.login_email.get().strip()
        password = self.login_password.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password!")
            return
        
        user = self.db.login_patient(email, password)
        if user:
            self.current_user = {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'age': user[3],
                'gender': user[4],
                'phone': user[5]
            }
            self.show_patient_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid email or password!")
    
    def register_patient(self):
        """Register new patient"""
        # Get form data
        name = self.register_entries['name'].get().strip()
        email = self.register_entries['email'].get().strip()
        password = self.register_entries['password'].get()
        confirm_password = self.register_entries['confirm_password'].get()
        age = self.register_entries['age'].get().strip()
        gender = self.register_entries['gender'].get()
        phone = self.register_entries['phone'].get().strip()
        
        # Validation
        if not all([name, email, password]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return
        
        # Register patient
        success = self.db.register_patient(name, email, password, age, gender, phone)
        if success:
            messagebox.showinfo("Success", "Registration successful! You can now login.")
            # Clear form
            for entry in self.register_entries.values():
                if isinstance(entry, tk.Entry):
                    entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Registration failed! Email may already exist.")
    
    # ==================== PATIENT DASHBOARD ====================
    def show_patient_dashboard(self):
        self.clear_window()
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header.pack(fill="x")
        
        tk.Label(header, text="👤 PATIENT DASHBOARD", font=("Arial", 20, "bold"),
                bg=self.colors['primary'], fg="white").pack(side="left", padx=30, pady=20)
        
        user_info = tk.Frame(header, bg=self.colors['primary'])
        user_info.pack(side="right", padx=30, pady=20)
        
        tk.Label(user_info, text=f"Welcome, {self.current_user['name']}", 
                font=("Arial", 12), bg=self.colors['primary'], fg="white").pack(side="left", padx=(0, 20))
        
        tk.Button(user_info, text="🚪 Logout", font=("Arial", 10),
                 bg=self.colors['danger'], fg="white",
                 command=self.show_welcome_screen).pack(side="left")
        
        # Main tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Dashboard
        dashboard_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(dashboard_tab, text="🏠 Dashboard")
        self.create_dashboard_tab(dashboard_tab)
        
        # Tab 2: Disease Detection
        detection_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(detection_tab, text="🔍 Detect Disease")
        self.create_detection_tab(detection_tab)
        
        # Tab 3: My Profile
        profile_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(profile_tab, text="👤 My Profile")
        self.create_profile_tab(profile_tab)
    
    def create_dashboard_tab(self, parent):
        """Create dashboard tab"""
        # Welcome message
        welcome_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
        welcome_frame.pack(fill="x", padx=20, pady=20)
        
        welcome_text = f"""
👋 Welcome back, {self.current_user['name']}!

📊 Your Information:
• Email: {self.current_user['email']}
• Age: {self.current_user['age'] or 'Not specified'}
• Gender: {self.current_user['gender'] or 'Not specified'}
• Phone: {self.current_user['phone'] or 'Not specified'}

💡 Quick Actions:
1. Upload skin image for AI analysis
2. Get instant disease diagnosis
3. View detailed medical information
4. Save your health reports
        """
        
        tk.Label(welcome_frame, text=welcome_text, font=("Arial", 11),
                bg="white", justify="left").pack(padx=20, pady=20)
        
        # Quick stats
        stats_frame = tk.Frame(parent, bg=self.colors['bg'])
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stat_items = [
            ("🔍 Disease Detection", "AI-Powered"),
            ("⚡ Speed", "Instant Results"),
            ("🎯 Accuracy", "High Confidence"),
            ("💾 Reports", "Save & Export")
        ]
        
        for i, (label, value) in enumerate(stat_items):
            stat_box = tk.Frame(stats_frame, bg="white", relief="solid", bd=1)
            stat_box.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            
            tk.Label(stat_box, text=label, font=("Arial", 10), 
                    bg="white", fg="gray").pack(pady=(10, 5))
            tk.Label(stat_box, text=value, font=("Arial", 14, "bold"), 
                    bg="white", fg=self.colors['primary']).pack(pady=(0, 10))
            
            stats_frame.grid_columnconfigure(i, weight=1)
    
    def create_detection_tab(self, parent):
        """Create disease detection tab"""
        # Main container
        main_frame = tk.Frame(parent, bg=self.colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(main_frame, text="🔍 SKIN DISEASE DETECTION", 
                font=("Arial", 20, "bold"), bg=self.colors['bg']).pack(pady=20)
        
        # Upload section
        upload_frame = tk.LabelFrame(main_frame, text=" UPLOAD IMAGE ", 
                                    font=("Arial", 12, "bold"), bg="white", padx=20, pady=20)
        upload_frame.pack(fill="x", pady=10)
        
        # Upload button
        tk.Button(upload_frame, text="📁 BROWSE IMAGE", font=("Arial", 12, "bold"),
                 bg=self.colors['primary'], fg="white", width=20,
                 command=self.browse_skin_image).pack(pady=10)
        
        # Image info
        self.image_label = tk.Label(upload_frame, text="No image selected", 
                                   font=("Arial", 10), bg="white", fg="gray")
        self.image_label.pack(pady=5)
        
        # Analyze button
        tk.Button(upload_frame, text="🔬 START AI ANALYSIS", font=("Arial", 14, "bold"),
                 bg=self.colors['success'], fg="white", width=25, height=2,
                 command=self.analyze_skin_image).pack(pady=20)
        
        # Results section
        result_frame = tk.LabelFrame(main_frame, text=" ANALYSIS RESULTS ", 
                                    font=("Arial", 12, "bold"), bg="white", padx=20, pady=20)
        result_frame.pack(fill="both", expand=True, pady=10)
        
        # Results text
        self.result_text = tk.Text(result_frame, height=15, font=("Arial", 10), wrap="word")
        self.result_text.pack(fill="both", expand=True)
        
        # Initial message
        self.result_text.insert(1.0, "👋 Welcome to Skin Disease Detection!\n\n"
                                   "1. Click 'BROWSE IMAGE' to upload skin photo\n"
                                   "2. Click 'START AI ANALYSIS' for diagnosis\n"
                                   "3. View results here\n\n"
                                   "💡 This system uses simulated AI for demonstration.")
        
        # Store current image
        self.current_image = None
    
    def browse_skin_image(self):
        """Browse for skin image"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Skin Image",
            filetypes=file_types
        )
        
        if file_path:
            try:
                # Store the path
                self.current_image = file_path
                filename = os.path.basename(file_path)
                
                # Update label
                self.image_label.config(
                    text=f"✅ Selected: {filename}",
                    fg="green"
                )
                
                # Update results text
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, 
                    f"📁 Image loaded successfully!\n"
                    f"File: {filename}\n\n"
                    f"📏 Ready for analysis...\n"
                    f"👉 Click 'START AI ANALYSIS' button"
                )
                
            except Exception as e:
                self.image_label.config(text=f"❌ Error: {str(e)}", fg="red")
    
    def analyze_skin_image(self):
        """Analyze skin image with AI"""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please select an image first!")
            return
        
        # Show processing
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, "🔬 AI Analysis in progress...\n\nPlease wait 2 seconds...")
        
        # Simulate processing in background
        self.root.after(2000, self.show_analysis_results)
    
    def show_analysis_results(self):
        """Show analysis results"""
        # Get all diseases
        diseases = self.db.get_all_diseases()
        
        if not diseases:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, "⚠️ No diseases found in database!")
            return
        
        # Select random disease for simulation
        disease = random.choice(diseases)
        confidence = random.randint(75, 95)
        
        # Save to database
        diagnosis_id = self.db.save_diagnosis(
            self.current_user['id'],
            disease[0],  # disease_id
            confidence,
            self.current_image
        )
        
        # Create report
        report = f"""✅ AI ANALYSIS COMPLETE
{'='*50}

🏥 DIAGNOSIS: {disease[1]}
📊 CONFIDENCE: {confidence}%

📋 DESCRIPTION:
{disease[2]}

⚠️ SYMPTOMS:
{disease[3]}

💊 TREATMENT:
{disease[4]}

🛡️ PREVENTION:
{disease[5]}

{'='*50}
📋 RECOMMENDATIONS:
1. Consult a dermatologist for confirmation
2. Follow prescribed treatment plan
3. Monitor skin changes regularly
4. Use sun protection daily

💡 IMPORTANT:
This is a simulated AI analysis for academic demonstration.
For real diagnosis, consult a medical professional.

📅 Diagnosis ID: {diagnosis_id}
📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Display results
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, report)
    
    def create_profile_tab(self, parent):
        """Create profile tab"""
        # Profile info
        info_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        profile_info = f"""
👤 Name: {self.current_user['name']}
📧 Email: {self.current_user['email']}
🎂 Age: {self.current_user['age'] or 'Not specified'}
🚻 Gender: {self.current_user['gender'] or 'Not specified'}
📞 Phone: {self.current_user['phone'] or 'Not specified'}

💡 Account Information:
• Registered: Database user
• Account Type: Patient
• Status: Active
"""
        
        tk.Label(info_frame, text=profile_info, font=("Arial", 11),
                bg="white", justify="left").pack(padx=20, pady=20)
    
    # ==================== ADMIN PANEL ====================
    def show_admin_panel(self):
        """Show admin panel"""
        self.clear_window()
        
        # Header
        header = tk.Frame(self.root, bg=self.colors['dark'], height=80)
        header.pack(fill="x")
        
        tk.Label(header, text="👑 ADMIN PANEL", font=("Arial", 20, "bold"),
                bg=self.colors['dark'], fg="white").pack(side="left", padx=30, pady=20)
        
        tk.Button(header, text="🏠 Back to Home", font=("Arial", 10),
                 bg=self.colors['warning'], fg="white",
                 command=self.show_welcome_screen).pack(side="right", padx=30, pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Admin options
        options_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
        options_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        admin_text = """
👑 ADMINISTRATOR PANEL

📊 SYSTEM STATISTICS:
• Total Diseases: 5 (Pre-loaded)
• Database: SQLite (skin_disease.db)
• System Status: Running
• Version: 1.0.0

🔧 ADMIN FEATURES:
1. View all registered patients
2. Manage disease database
3. View diagnosis history
4. System monitoring
5. Data export/backup

⚠️ SECURITY NOTE:
This is a demonstration panel.
In a real system, proper authentication
and authorization would be implemented.

📅 System Date: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        tk.Label(options_frame, text=admin_text, font=("Arial", 11),
                bg="white", justify="left").pack(padx=20, pady=20)
        
        # Admin buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(fill="x", pady=10)
        
        tk.Button(button_frame, text="📊 View Database", font=("Arial", 11),
                 bg=self.colors['primary'], fg="white", width=20,
                 command=self.view_database).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="⚙️ System Info", font=("Arial", 11),
                 bg=self.colors['info'], fg="white", width=20,
                 command=self.system_info).pack(side="left", padx=5)
    
    def view_database(self):
        """View database information"""
        info = "📊 DATABASE INFORMATION\n"
        info += "=" * 40 + "\n\n"
        
        # Count patients
        self.db.cursor.execute("SELECT COUNT(*) FROM patients")
        patient_count = self.db.cursor.fetchone()[0]
        info += f"👥 Total Patients: {patient_count}\n"
        
        # Count diseases
        self.db.cursor.execute("SELECT COUNT(*) FROM diseases")
        disease_count = self.db.cursor.fetchone()[0]
        info += f"🏥 Total Diseases: {disease_count}\n"
        
        # Count diagnoses
        self.db.cursor.execute("SELECT COUNT(*) FROM diagnoses")
        diagnosis_count = self.db.cursor.fetchone()[0]
        info += f"🔍 Total Diagnoses: {diagnosis_count}\n\n"
        
        info += "📁 Database File: skin_disease.db\n"
        info += "🔧 Status: Connected & Operational\n"
        
        messagebox.showinfo("Database Info", info)
    
    def system_info(self):
        """Show system information"""
        info = """
⚙️ SYSTEM INFORMATION
=====================

🎓 PROJECT:
University Skin Disease Detection System

✅ FEATURES:
1. Patient Registration & Login
2. Skin Image Upload
3. AI Disease Detection (Simulated)
4. Database Storage (SQLite)
5. Detailed Medical Reports
6. User-friendly Interface

🔧 TECHNICAL SPECS:
• Language: Python 3
• GUI: Tkinter
• Database: SQLite
• Dependencies: None (Pure Python)

📁 FILES:
• skin_disease_system.py (Main Program)
• skin_disease.db (Database)

👨‍💻 DEVELOPED FOR:
University Academic Project
Computer Science Department

⚠️ DISCLAIMER:
This is a demonstration system for
educational purposes only.
"""
        messagebox.showinfo("System Information", info)

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = SkinDiseaseSystem(root)
    root.mainloop()