"""
PyTech Arena - Complete Backend System
All backend functionality consolidated into a single file
"""

import os
import json
import csv
import io
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, Response
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import frontend templates
try:
    from frontend import get_template
except ImportError:
    # Fallback if frontend.py is not available
    def get_template(template_name):
        return "<h1>Template not found</h1><p>Please ensure frontend.py is available</p>"

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pytech_arena.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Firebase Configuration (if available)
FIREBASE_AVAILABLE = False
try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_AVAILABLE = True
except ImportError:
    print("Firebase not available, using SQLite only")

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    company_name = db.Column(db.String(200))

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department = db.Column(db.String(100))
    gpa = db.Column(db.Float)
    skills = db.Column(db.Text)
    internships = db.Column(db.Text)
    projects = db.Column(db.Text)
    certifications = db.Column(db.Text)
    career_preferences = db.Column(db.Text)
    placement_status = db.Column(db.String(50), default='Not Placed')
    resume_path = db.Column(db.String(500))
    photo_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(200))
    job_type = db.Column(db.String(50))
    salary_range = db.Column(db.String(100))
    eligibility = db.Column(db.Text)
    application_process = db.Column(db.Text)
    visit_date = db.Column(db.Date)
    visit_time = db.Column(db.String(50))
    venue = db.Column(db.String(200))
    deadline = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(50))
    description = db.Column(db.Text)
    website = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))
    headquarters = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)
    status = db.Column(db.String(50), default='Applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

# Firebase Manager (if available)
class FirebaseManager:
    def __init__(self):
        self.db = None
        if FIREBASE_AVAILABLE and os.getenv('FIREBASE_CREDENTIALS_PATH'):
            try:
                cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
                firebase_admin.initialize_app(cred, {
                    'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
                })
                self.db = db.reference()
                print("✅ Firebase initialized successfully")
            except Exception as e:
                print(f"❌ Firebase initialization failed: {e}")
    
    def get_users(self):
        if self.db:
            try:
                return self.db.child('users').get()
            except:
                return None
        return None
    
    def get_student_profiles(self):
        if self.db:
            try:
                return self.db.child('student_profiles').get()
            except:
                return None
        return None
    
    def get_job_applications(self):
        if self.db:
            try:
                return self.db.child('job_applications').get()
            except:
                return None
        return None

# Initialize Firebase Manager
firebase_manager = FirebaseManager()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Decorators for role-based access
def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Try Firebase first, then SQLite
        user = None
        
        if firebase_manager.db:
            users_data = firebase_manager.get_users()
            if users_data:
                for uid, user_data in users_data.items():
                    if user_data.get('email') == email:
                        # Simple password check (in production, use proper hashing)
                        if check_password_hash(user_data.get('password_hash', ''), password):
                            user = User()
                            user.id = uid
                            user.name = user_data.get('name')
                            user.email = user_data.get('email')
                            user.role = user_data.get('role')
                            break
        
        if not user:
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                pass
            else:
                user = None
        
        if user:
            login_user(user)
            user.last_login = datetime.utcnow()
            if isinstance(user.id, str) and firebase_manager.db:
                # Update Firebase
                firebase_manager.db.child('users').child(user.id).update({
                    'last_login': user.last_login.isoformat()
                })
            else:
                # Update SQLite
                db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template_string(get_template('login.html'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        # Check if user exists
        existing_user = None
        
        if firebase_manager.db:
            users_data = firebase_manager.get_users()
            if users_data:
                for uid, user_data in users_data.items():
                    if user_data.get('email') == email:
                        existing_user = True
                        break
        
        if not existing_user:
            existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Email already registered', 'danger')
        else:
            password_hash = generate_password_hash(password)
            
            if firebase_manager.db:
                # Create in Firebase
                new_user_ref = firebase_manager.db.child('users').push({
                    'name': name,
                    'email': email,
                    'password_hash': password_hash,
                    'role': role,
                    'created_at': datetime.utcnow().isoformat()
                })
                
                user = User()
                user.id = new_user_ref.key
                user.name = name
                user.email = email
                user.role = role
            else:
                # Create in SQLite
                user = User(name=name, email=email, password_hash=password_hash, role=role)
                db.session.add(user)
                db.session.commit()
            
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template_string(get_template('register.html'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Main Routes
@app.route('/')
def home():
    return render_template_string(get_template('index.html'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('student_dashboard'))
    elif current_user.role == 'recruiter':
        return redirect(url_for('recruiter_dashboard'))
    else:
        return redirect(url_for('home'))

# Admin Routes
@app.route('/admin/dashboard')
@login_required
@roles_required('admin')
def admin_dashboard():
    # Get statistics
    total_students = StudentProfile.query.count()
    placed_students = StudentProfile.query.filter(StudentProfile.placement_status != 'Not Placed').count()
    total_recruiters = User.query.filter_by(role='recruiter').count()
    
    # Department statistics
    dept_stats = db.session.query(
        StudentProfile.department,
        db.func.count(StudentProfile.id).label('count'),
        db.func.avg(StudentProfile.gpa).label('avg_gpa')
    ).group_by(StudentProfile.department).all()
    
    placement_rate = (placed_students / total_students * 100) if total_students > 0 else 0
    
    return render_template_string(get_template('admin_dashboard.html'),
                         total_students=total_students,
                         placed_students=placed_students,
                         total_recruiters=total_recruiters,
                         placement_rate=placement_rate,
                         dept_stats=dept_stats)

@app.route('/admin/students')
@login_required
@roles_required('admin')
def admin_students():
    students = db.session.query(User, StudentProfile).join(StudentProfile, User.id == StudentProfile.user_id).filter(User.role == 'student').all()
    return render_template_string(get_template('admin_students.html'), students=students)

@app.route('/admin/recruiters')
@login_required
@roles_required('admin')
def admin_recruiters():
    recruiters = User.query.filter_by(role='recruiter').all()
    return render_template_string(get_template('admin_recruiters.html'), recruiters=recruiters)

@app.route('/admin/analytics')
@login_required
@roles_required('admin')
def admin_analytics():
    # Get comprehensive analytics data
    total_students = StudentProfile.query.count()
    placed_students = StudentProfile.query.filter(StudentProfile.placement_status != 'Not Placed').count()
    not_placed_students = total_students - placed_students
    
    # Department statistics
    dept_stats = {}
    dept_query = db.session.query(
        StudentProfile.department,
        db.func.count(StudentProfile.id).label('count'),
        db.func.avg(StudentProfile.gpa).label('avg_gpa')
    ).group_by(StudentProfile.department).all()
    
    for dept, count, avg_gpa in dept_query:
        dept_stats[dept] = {
            'count': count,
            'avg_gpa': round(avg_gpa, 2) if avg_gpa else 0
        }
    
    total_recruiters = User.query.filter_by(role='recruiter').count()
    placement_rate = (placed_students / total_students * 100) if total_students > 0 else 0
    
    return render_template_string(get_template('admin_analytics.html'),
                         total_students=total_students,
                         placed_students=placed_students,
                         not_placed_students=not_placed_students,
                         placement_rate=placement_rate,
                         dept_stats=dept_stats,
                         total_recruiters=total_recruiters,
                         recent_students=0)

@app.route('/admin/analytics/export')
@login_required
@roles_required('admin')
def admin_analytics_export():
    # Export analytics data as CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['PyTech Arena Analytics Report'])
    writer.writerow(['Generated on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Overall Statistics
    total_students = StudentProfile.query.count()
    placed_students = StudentProfile.query.filter(StudentProfile.placement_status != 'Not Placed').count()
    
    writer.writerow(['Overall Statistics'])
    writer.writerow(['Total Students', total_students])
    writer.writerow(['Placed Students', placed_students])
    writer.writerow(['Placement Rate (%)', round((placed_students/total_students*100), 1) if total_students > 0 else 0])
    writer.writerow([])
    
    # Department-wise Statistics
    writer.writerow(['Department-wise Statistics'])
    writer.writerow(['Department', 'Total Students', 'Average GPA'])
    
    dept_query = db.session.query(
        StudentProfile.department,
        db.func.count(StudentProfile.id).label('count'),
        db.func.avg(StudentProfile.gpa).label('avg_gpa')
    ).group_by(StudentProfile.department).all()
    
    for dept, count, avg_gpa in dept_query:
        writer.writerow([dept, count, round(avg_gpa, 2) if avg_gpa else 0])
    
    # Create response
    output.seek(0)
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=analytics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/admin/recruiters/export')
@login_required
@roles_required('admin')
def admin_export_recruiters():
    # Export recruiters data as CSV
    recruiters = User.query.filter_by(role='recruiter').all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Company', 'Registration Date', 'Last Login'])
    
    for recruiter in recruiters:
        writer.writerow([
            recruiter.id,
            recruiter.name,
            recruiter.email,
            getattr(recruiter, 'company_name', 'Not specified'),
            recruiter.created_at.strftime('%Y-%m-%d') if recruiter.created_at else 'N/A',
            recruiter.last_login.strftime('%Y-%m-%d %H:%M') if recruiter.last_login else 'Never'
        ])
    
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=recruiters_export.csv"}
    )

@app.route('/admin/recruiter/<recruiter_id>/edit', methods=['POST'])
@login_required
@roles_required('admin')
def admin_edit_recruiter(recruiter_id):
    recruiter = User.query.get_or_404(recruiter_id)
    
    if recruiter.role != 'recruiter':
        flash('Invalid user.', 'danger')
        return redirect(url_for('admin_recruiters'))
    
    recruiter.name = request.form.get('name')
    recruiter.email = request.form.get('email')
    recruiter.company_name = request.form.get('company_name')
    
    db.session.commit()
    flash('Recruiter updated successfully.', 'success')
    return redirect(url_for('admin_recruiters'))

@app.route('/admin/recruiter/<int:recruiter_id>/delete', methods=['POST'])
@login_required
@roles_required('admin')
def admin_delete_recruiter(recruiter_id):
    recruiter = User.query.get_or_404(recruiter_id)
    
    if recruiter.role != 'recruiter':
        flash('Invalid user.', 'danger')
        return redirect(url_for('admin_recruiters'))
    
    db.session.delete(recruiter)
    db.session.commit()
    flash('Recruiter deleted successfully.', 'success')
    return redirect(url_for('admin_recruiters'))

# Student Routes
@app.route('/student/dashboard')
@login_required
@roles_required('student')
def student_dashboard():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    return render_template_string(get_template('student_dashboard.html'), profile=profile)

@app.route('/student/edit', methods=['GET', 'POST'])
@login_required
@roles_required('student')
def student_edit():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        if not profile:
            profile = StudentProfile(user_id=current_user.id)
            db.session.add(profile)
        
        profile.department = request.form.get('department')
        profile.gpa = float(request.form.get('gpa', 0))
        profile.skills = request.form.get('skills')
        profile.internships = request.form.get('internships')
        profile.projects = request.form.get('projects')
        profile.certifications = request.form.get('certifications')
        profile.career_preferences = request.form.get('career_preferences')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template_string(get_template('student_edit.html'), profile=profile)

@app.route('/student/status')
@login_required
@roles_required('student')
def student_status():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    # Mock opportunities data
    opportunities = [
        {
            "title": "Software Engineer at TechCorp",
            "type": "Full-time",
            "location": "Remote",
            "salary": "$80,000 - $120,000",
            "status": "Open"
        },
        {
            "title": "Frontend Developer at StartupXYZ",
            "type": "Full-time",
            "location": "Hybrid",
            "salary": "$70,000 - $100,000",
            "status": "Applied"
        }
    ]
    
    return render_template_string(get_template('student_status.html'), profile=profile, opportunities=opportunities)

# Recruiter Routes
@app.route('/recruiter/dashboard')
@login_required
@roles_required('recruiter')
def recruiter_dashboard():
    jobs = JobPosting.query.filter_by(company_id=current_user.id).all()
    return render_template_string(get_template('recruiter_dashboard.html'), jobs=jobs)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template_string(get_template('404.html')), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template_string(get_template('500.html')), 500

# Initialize database
with app.app_context():
    db.create_all()
    
    # Create default admin user if not exists
    admin = User.query.filter_by(email='placement@jntugv.edu.in').first()
    if not admin:
        admin = User(
            name='Dr. Ramesh Kumar',
            email='placement@jntugv.edu.in',
            password_hash=generate_password_hash('Admin@2026'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
