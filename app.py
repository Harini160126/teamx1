from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from functools import wraps
import os
import json
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Firebase modules
try:
    from firebase_config import initialize_firebase
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️ Firebase modules not available, using SQLite only")

# Import database manager
from database_manager import get_database_manager


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app = Flask(__name__)

# Load configuration from environment variables
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "placement.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))  # 16MB
app.config["ALLOWED_EXTENSIONS"] = {
    "pdf", "doc", "docx", "txt", "jpg", "jpeg", "png", "gif"
}

# Email configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")

# Debug mode
app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Database type configuration
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()

# Initialize Firebase if enabled
firebase_managers = None
if DATABASE_TYPE == "firebase" and FIREBASE_AVAILABLE:
    firebase_managers = initialize_firebase()
    if firebase_managers:
        print("✅ Firebase database initialized")
    else:
        print("❌ Firebase initialization failed, falling back to SQLite")
        DATABASE_TYPE = "sqlite"

print(f"🗄️ Using database: {DATABASE_TYPE}")

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/placement_system.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Placement System startup')

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    # Handle Firebase string IDs and SQLite integer IDs
    if database_manager.db_type == "firebase":
        # For Firebase, get user from database manager
        try:
            # Access the Firebase manager through the user_manager.firebase
            firebase_manager = database_manager.user_manager.firebase
            users = firebase_manager.get_reference('users').get()
            if users:
                for uid, user_data in users.items():
                    if uid == user_id:
                        # Create a temporary User object for Flask-Login
                        temp_user = User()
                        temp_user.id = uid
                        temp_user.name = user_data['name']
                        temp_user.email = user_data['email']
                        temp_user.role = user_data['role']
                        return temp_user
            return None
        except Exception as e:
            app.logger.error(f'Error loading user from Firebase: {str(e)}')
            return None
    else:
        # For SQLite, use the original method
        try:
            return User.query.get(int(user_id))
        except ValueError:
            return None

# Initialize database manager
database_manager = None
if DATABASE_TYPE == "firebase" and firebase_managers:
    database_manager = get_database_manager("firebase", firebase_managers=firebase_managers)
else:
    # We'll initialize SQLite database manager after models are defined
    pass

print(f"✅ Database manager initialization setup complete")


class User(db.Model, UserMixin):
    id = db.Column(db.String(50), primary_key=True)  # Changed to String for Firebase compatibility
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'admin', 'recruiter'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship("StudentProfile", backref="user", uselist=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey("user.id"), nullable=False)  # Changed to String for Firebase compatibility
    department = db.Column(db.String(100), nullable=False)
    gpa = db.Column(db.Float, nullable=False)
    skills = db.Column(db.String(255), nullable=True)
    internships = db.Column(db.Text, nullable=True)
    projects = db.Column(db.Text, nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    career_preferences = db.Column(db.Text, nullable=True)
    resume_filename = db.Column(db.String(255), nullable=True)
    photo_filename = db.Column(db.String(255), nullable=True)
    placement_status = db.Column(db.String(100), default="Not Placed")
    # Contact details
    phone = db.Column(db.String(20), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    portfolio = db.Column(db.String(255), nullable=True)


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey("job_posting.id"), nullable=True)  # New foreign key
    job_id = db.Column(db.String(50), nullable=False)  # Keep for backward compatibility
    company_name = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.String(20), nullable=False)
    skills = db.Column(db.Text, nullable=True)
    cover_letter = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Pending")  # Pending, Reviewed, Shortlisted, Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship("User", backref="job_applications")
    job_posting = db.relationship("JobPosting", backref="job_applications")


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    headquarters = db.Column(db.String(200), nullable=True)
    employees = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    logo_letter = db.Column(db.String(10), default="C")
    gradient = db.Column(db.String(200), default="linear-gradient(135deg, #0033a0 0%, #00b4d8 100%)")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    job_postings = db.relationship("JobPosting", backref="company", lazy=True, cascade="all, delete-orphan")


class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)  # Full-time, Internship, Part-time
    salary_range = db.Column(db.String(100), nullable=True)
    eligibility = db.Column(db.Text, nullable=True)
    application_process = db.Column(db.Text, nullable=True)
    visit_date = db.Column(db.DateTime, nullable=True)
    visit_time = db.Column(db.String(100), nullable=True)
    venue = db.Column(db.String(200), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default="info")  # info, success, warning, error
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref="notifications")


class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    participating_companies = db.relationship("Company", secondary="drive_companies", backref="drives")


drive_companies = db.Table('drive_companies',
    db.Column('drive_id', db.Integer, db.ForeignKey('placement_drive.id'), primary_key=True),
    db.Column('company_id', db.Integer, db.ForeignKey('company.id'), primary_key=True)
)

# Initialize SQLite database manager if needed
if database_manager is None:
    models = {
        'User': User,
        'StudentProfile': StudentProfile,
        'JobPosting': JobPosting,
        'JobApplication': JobApplication,
        'Notification': Notification
    }
    database_manager = get_database_manager("sqlite", db=db, models=models)
    print(f"✅ SQLite database manager initialized")

print(f"🗄️ Final database type: {database_manager.db_type}")


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def create_notification(user_id, title, message, notification_type="info"):
    """Create a notification for a user."""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type
    )
    db.session.add(notification)
    db.session.commit()


def get_unread_notification_count(user_id):
    """Get count of unread notifications for a user."""
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()


def validate_student_profile(profile):
    """Validate student profile data."""
    errors = []
    
    if not profile.department or len(profile.department.strip()) < 2:
        errors.append("Department is required")
    
    if profile.gpa is None or profile.gpa < 0 or profile.gpa > 10:
        errors.append("GPA must be between 0 and 10")
    
    if profile.gpa < 6.0:
        errors.append("GPA should be at least 6.0 for placement eligibility")
    
    return errors


def validate_email(email):
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format."""
    import re
    pattern = r'^[+]?[0-9]{10,15}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password):
    """Validate password strength."""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    return errors


def sanitize_input(text):
    """Sanitize user input to prevent XSS."""
    if not text:
        return ""
    
    # Basic XSS prevention
    dangerous_chars = ["<", ">", "&", '"', "'", "/"]
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    app.logger.warning(f'404 Not Found: {request.url}')
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    app.logger.error(f'500 Internal Server Error: {str(error)}')
    return render_template('500.html'), 500


@app.errorhandler(413)
def too_large(error):
    """Handle file too large errors."""
    flash('File too large. Maximum size is 16MB.', 'danger')
    return redirect(request.referrer or url_for('index'))


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all other exceptions."""
    # Pass through HTTP exceptions
    if isinstance(e, HTTPException):
        return e
    
    app.logger.error(f'Unhandled Exception: {str(e)}')
    
    if request.is_json:
        return jsonify({"error": "Internal server error"}), 500
    
    return render_template('500.html'), 500


# Input validation decorator
def validate_form_fields(required_fields):
    """Decorator to validate required form fields."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for field in required_fields:
                if not request.form.get(field) or not request.form.get(field).strip():
                    flash(f'{field.replace("_", " ").title()} is required.', 'danger')
                    return redirect(request.referrer or url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_placement_report():
    """Generate comprehensive placement report."""
    total_students = StudentProfile.query.count()
    placed_students = StudentProfile.query.filter(StudentProfile.placement_status != "Not Placed").count()
    
    # Department-wise statistics
    dept_stats = db.session.query(
        StudentProfile.department,
        db.func.count(StudentProfile.id).label('total'),
        db.func.sum(db.case([(StudentProfile.placement_status != "Not Placed", 1)], else_=0)).label('placed'),
        db.func.avg(StudentProfile.gpa).label('avg_gpa')
    ).group_by(StudentProfile.department).all()
    
    # Company-wise placements
    company_stats = db.session.query(
        JobApplication.company_name,
        db.func.count(JobApplication.id).label('applications'),
        db.func.sum(db.case([(JobApplication.status == "Shortlisted", 1)], else_=0)).label('shortlisted')
    ).group_by(JobApplication.company_name).all()
    
    return {
        'total_students': total_students,
        'placed_students': placed_students,
        'placement_rate': (placed_students / total_students * 100) if total_students > 0 else 0,
        'dept_stats': dept_stats,
        'company_stats': company_stats
    }


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get("role")
            if user_role not in roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("index"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.context_processor
def inject_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return {"current_user": None, "notification_count": 0}
    user = User.query.get(user_id)
    notification_count = get_unread_notification_count(user_id) if user else 0
    return {"current_user": user, "notification_count": notification_count}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = sanitize_input(request.form.get("name"))
        email = sanitize_input(request.form.get("email"))
        password = request.form.get("password")
        role = request.form.get("role", "student")
        
        # Validate inputs
        errors = []
        
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        
        if not validate_email(email):
            errors.append("Please enter a valid email address")
        
        password_errors = validate_password_strength(password)
        errors.extend(password_errors)
        
        if errors:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for("register"))
        
        # Prevent users from registering as admin unless there's no admin yet
        if role == "admin" and database_manager.get_user_by_email("placement@jntugv.edu.in"):
            role = "student"

        # Check if user already exists using database manager
        if database_manager.get_user_by_email(email):
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))

        try:
            # Use database manager to create user (automatically syncs to Firebase)
            user_id = database_manager.create_user(name, email, password, role)
            
            app.logger.info(f'New user registered: {email} with role {role}')
            flash("Registration successful. Please login.", "success")
            
            # Create welcome notification for the new user
            if role == "student":
                database_manager.create_notification(
                    user_id, 
                    "Welcome to PyTech Arena!", 
                    f"Welcome {name}! Your account has been created successfully. Complete your profile to apply for jobs.",
                    "success"
                )
            
            return redirect(url_for("login"))
            
        except Exception as e:
            app.logger.error(f'Registration error: {str(e)}')
            flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Use database manager to verify user
        user = database_manager.verify_password(email, password)
        if not user:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        # Create a temporary user object for Flask-Login
        temp_user = User()
        temp_user.id = user['id']
        temp_user.name = user['name']
        temp_user.email = user['email']
        temp_user.role = user['role']

        # Use Flask-Login to manage session
        login_user(temp_user)
        session["user_id"] = user['id']
        session["role"] = user['role']

        flash("Logged in successfully.", "success")

        if user['role'] == "admin":
            return redirect(url_for("admin_dashboard"))
        elif user['role'] == "recruiter":
            return redirect(url_for("recruiter_dashboard"))
        else:
            return redirect(url_for("student_dashboard"))

    return render_template("login_fixed.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/student/dashboard")
@login_required
@roles_required("student")
def student_dashboard():
    user_id = session["user_id"]
    
    # Get profile from Firebase or SQLite based on database type
    if database_manager.db_type == "firebase":
        profile = database_manager.get_student_profile(user_id)
    else:
        profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    return render_template("student_dashboard.html", profile=profile)


@app.route("/student/profile", methods=["GET", "POST"])
@login_required
@roles_required("student")
def student_profile():
    user_id = session["user_id"]
    
    # Get profile from Firebase or SQLite based on database type
    if database_manager.db_type == "firebase":
        profile = database_manager.get_student_profile(user_id)
    else:
        profile = StudentProfile.query.filter_by(user_id=user_id).first()

    if request.method == "POST":
        profile.department = request.form.get("department")
        profile.gpa = float(request.form.get("gpa") or 0.0)
        profile.skills = request.form.get("skills")
        profile.internships = request.form.get("internships")
        profile.projects = request.form.get("projects")
        profile.certifications = request.form.get("certifications")
        profile.career_preferences = request.form.get("career_preferences")
        
        # Contact details
        profile.phone = request.form.get("phone")
        profile.linkedin = request.form.get("linkedin")
        profile.github = request.form.get("github")
        profile.portfolio = request.form.get("portfolio")
        
        # Handle file uploads
        if 'resume' in request.files:
            resume = request.files['resume']
            if resume and allowed_file(resume.filename):
                filename = secure_filename(resume.filename)
                resume.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile.resume_filename = filename
        
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile.photo_filename = filename
        
        # Save to Firebase or SQLite
        if database_manager.db_type == "firebase":
            # Update Firebase profile
            profile_data = {
                'department': profile.department,
                'gpa': profile.gpa,
                'skills': profile.skills,
                'internships': profile.internships,
                'projects': profile.projects,
                'certifications': profile.certifications,
                'career_preferences': profile.career_preferences,
                'phone': profile.phone,
                'linkedin': profile.linkedin,
                'github': profile.github,
                'portfolio': profile.portfolio,
                'resume_filename': profile.resume_filename,
                'photo_filename': profile.photo_filename,
                'updated_at': datetime.utcnow().isoformat()
            }
            database_manager.update_student_profile(profile.id, profile_data)
        else:
            # Update SQLite
            db.session.commit()
        
            photo_filename = f"photo_{user_id}_{int(datetime.utcnow().timestamp())}_{filename}"
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
            photo.save(photo_path)
            
            # Basic file validation
            if os.path.getsize(photo_path) > 5 * 1024 * 1024:  # 5MB limit for images
                os.remove(photo_path)
                flash("Image file too large. Maximum size is 5MB.", "danger")
                return redirect(url_for("student_profile"))
            
            profile.photo_filename = photo_filename

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("student_profile.html", profile=profile)


@app.route("/admin/dashboard")
@login_required
@roles_required("admin")
def admin_dashboard():
    # Get statistics from Firebase or SQLite based on database type
    if database_manager.db_type == "firebase":
        # Firebase statistics
        # Get all student profiles from Firebase
        profiles_ref = database_manager.profile_manager.firebase.get_reference('student_profiles').get()
        all_profiles = list(profiles_ref.values()) if profiles_ref else []
        
        total_students = len(all_profiles) if all_profiles else 0
        placed_students = len([p for p in all_profiles if p.get('placement_status') != 'Not Placed']) if all_profiles else 0
        
        # Department-wise statistics
        dept_stats = {}
        if all_profiles:
            for profile in all_profiles:
                dept = profile.get('department', 'Unknown')
                if dept not in dept_stats:
                    dept_stats[dept] = {
                        'total': 0,
                        'placed': 0,
                        'avg_gpa': 0.0,
                        'gpa_sum': 0.0
                    }
                dept_stats[dept]['total'] += 1
                if profile.get('placement_status') != 'Not Placed':
                    dept_stats[dept]['placed'] += 1
                gpa = profile.get('gpa', 0.0)
                if gpa:
                    dept_stats[dept]['gpa_sum'] += gpa
            
            # Calculate averages
            for dept, stats in dept_stats.items():
                if stats['total'] > 0:
                    stats['avg_gpa'] = round(stats['gpa_sum'] / stats['total'], 2)
                stats['placement_rate'] = round((stats['placed'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0
        
        # Get recent applications
        applications_ref = database_manager.job_manager.firebase.get_reference('job_applications').get()
        recent_applications = list(applications_ref.values())[:10] if applications_ref else []  # Last 10 applications
        
    else:
        # SQLite statistics
        total_students = StudentProfile.query.count()
        placed_students = StudentProfile.query.filter(StudentProfile.placement_status != "Not Placed").count()
        
        # Department-wise statistics
        dept_stats = {}
        dept_query = db.session.query(
            StudentProfile.department,
            db.func.count(StudentProfile.id).label('total'),
            db.func.sum(db.case([(StudentProfile.placement_status != "Not Placed", 1)], else_=0)).label('placed'),
            db.func.avg(StudentProfile.gpa).label('avg_gpa')
        ).group_by(StudentProfile.department).all()
        
        for dept, total, placed, avg_gpa in dept_query:
            dept_stats[dept] = {
                'total': total,
                'placed': placed,
                'avg_gpa': round(avg_gpa, 2) if avg_gpa else 0.0,
                'placement_rate': round((placed / total * 100), 1) if total > 0 else 0
            }
        
        recent_applications = JobApplication.query.order_by(JobApplication.applied_at.desc()).limit(10).all()
    
    placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 0
    
    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        placed_students=placed_students,
        placement_rate=placement_rate,
        dept_stats=dept_stats,
        recent_applications=recent_applications
    )


@app.route("/admin/export-report")
@login_required
@roles_required("admin")
def admin_export_report():
    """Export placement statistics report as CSV."""
    import csv
    from io import StringIO
    from flask import Response
    
    # Get statistics from Firebase or SQLite based on database type
    if database_manager.db_type == "firebase":
        # Firebase data
        profiles_ref = database_manager.profile_manager.firebase.get_reference('student_profiles').get()
        all_profiles = list(profiles_ref.values()) if profiles_ref else []
        
        applications_ref = database_manager.job_manager.firebase.get_reference('job_applications').get()
        all_applications = list(applications_ref.values()) if applications_ref else []
        
        # Prepare CSV data
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['PyTech Arena Placement Report'])
        writer.writerow(['Generated on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Overall Statistics
        total_students = len(all_profiles) if all_profiles else 0
        placed_students = len([p for p in all_profiles if p.get('placement_status') != 'Not Placed']) if all_profiles else 0
        placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 0
        
        writer.writerow(['Overall Statistics'])
        writer.writerow(['Total Students', total_students])
        writer.writerow(['Placed Students', placed_students])
        writer.writerow(['Placement Rate (%)', placement_rate])
        writer.writerow([])
        
        # Department-wise Statistics
        writer.writerow(['Department-wise Statistics'])
        writer.writerow(['Department', 'Total Students', 'Placed Students', 'Placement Rate (%)', 'Average GPA'])
        
        dept_stats = {}
        if all_profiles:
            for profile in all_profiles:
                dept = profile.get('department', 'Unknown')
                if dept not in dept_stats:
                    dept_stats[dept] = {'total': 0, 'placed': 0, 'gpa_sum': 0.0}
                dept_stats[dept]['total'] += 1
                if profile.get('placement_status') != 'Not Placed':
                    dept_stats[dept]['placed'] += 1
                gpa = profile.get('gpa', 0.0)
                if gpa:
                    dept_stats[dept]['gpa_sum'] += gpa
            
            for dept, stats in dept_stats.items():
                avg_gpa = round(stats['gpa_sum'] / stats['total'], 2) if stats['total'] > 0 else 0
                placement_rate = round((stats['placed'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0
                writer.writerow([dept, stats['total'], stats['placed'], placement_rate, avg_gpa])
        
        writer.writerow([])
        
        # Student Details
        writer.writerow(['Student Details'])
        writer.writerow(['Name', 'Email', 'Department', 'GPA', 'Placement Status', 'Skills'])
        
        if all_profiles:
            for profile in all_profiles:
                writer.writerow([
                    profile.get('full_name', 'N/A'),
                    profile.get('email', 'N/A'),
                    profile.get('department', 'N/A'),
                    profile.get('gpa', 0.0),
                    profile.get('placement_status', 'Not Placed'),
                    profile.get('skills', 'N/A')
                ])
        
        writer.writerow([])
        
        # Recent Applications
        writer.writerow(['Recent Job Applications'])
        writer.writerow(['Student Name', 'Job Title', 'Company', 'Status', 'Applied Date'])
        
        if all_applications:
            for app in all_applications[:20]:  # Last 20 applications
                writer.writerow([
                    app.get('full_name', 'N/A'),
                    app.get('job_title', 'N/A'),
                    app.get('company_name', 'N/A'),
                    app.get('status', 'Applied'),
                    app.get('applied_at', 'N/A')
                ])
    
    else:
        # SQLite data
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['PyTech Arena Placement Report'])
        writer.writerow(['Generated on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Overall Statistics
        total_students = StudentProfile.query.count()
        placed_students = StudentProfile.query.filter(StudentProfile.placement_status != "Not Placed").count()
        placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 0
        
        writer.writerow(['Overall Statistics'])
        writer.writerow(['Total Students', total_students])
        writer.writerow(['Placed Students', placed_students])
        writer.writerow(['Placement Rate (%)', placement_rate])
        writer.writerow([])
        
        # Department-wise Statistics
        writer.writerow(['Department-wise Statistics'])
        writer.writerow(['Department', 'Total Students', 'Placed Students', 'Placement Rate (%)', 'Average GPA'])
        
        dept_query = db.session.query(
            StudentProfile.department,
            db.func.count(StudentProfile.id).label('total'),
            db.func.sum(db.case([(StudentProfile.placement_status != "Not Placed", 1)], else_=0)).label('placed'),
            db.func.avg(StudentProfile.gpa).label('avg_gpa')
        ).group_by(StudentProfile.department).all()
        
        for dept, total, placed, avg_gpa in dept_query:
            placement_rate = round((placed / total * 100), 1) if total > 0 else 0
            writer.writerow([dept, total, placed, placement_rate, round(avg_gpa, 2) if avg_gpa else 0.0])
        
        writer.writerow([])
        
        # Student Details
        writer.writerow(['Student Details'])
        writer.writerow(['Name', 'Email', 'Department', 'GPA', 'Placement Status', 'Skills'])
        
        students = db.session.query(StudentProfile, User).join(User).all()
        for profile, user in students:
            writer.writerow([
                user.name,
                user.email,
                profile.department,
                profile.gpa,
                profile.placement_status,
                profile.skills or 'N/A'
            ])
        
        writer.writerow([])
        
        # Recent Applications
        writer.writerow(['Recent Job Applications'])
        writer.writerow(['Student Name', 'Job Title', 'Company', 'Status', 'Applied Date'])
        
        applications = JobApplication.query.order_by(JobApplication.applied_at.desc()).limit(20).all()
        for app in applications:
            writer.writerow([
                app.full_name,
                app.job_title,
                app.company_name,
                app.status,
                app.applied_at.strftime('%Y-%m-%d %H:%M:%S') if app.applied_at else 'N/A'
            ])
    
    # Create response
    output.seek(0)
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=placement_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response


@app.route("/admin/student/<int:student_id>/status", methods=["POST"])
@login_required
@roles_required("admin")
def admin_update_status(student_id):
    if database_manager.db_type == "firebase":
        # Firebase implementation
        profile = database_manager.get_student_profile(str(student_id))
        if profile:
            status = request.form.get("placement_status")
            database_manager.update_student_profile(str(student_id), {'placement_status': status})
            flash("Placement status updated.", "success")
        else:
            flash("Student profile not found.", "danger")
    else:
        # SQLite implementation
        profile = StudentProfile.query.get_or_404(student_id)
        status = request.form.get("placement_status")
        profile.placement_status = status
        db.session.commit()
        flash("Placement status updated.", "success")
    
    return redirect(url_for("admin_students"))


@app.route("/admin/management")
@login_required
@roles_required("admin")
def admin_management():
    """Admin management dashboard for students and recruiters."""
    total_students = StudentProfile.query.count()
    placed_students = StudentProfile.query.filter(StudentProfile.placement_status != "Not Placed").count()
    total_recruiters = User.query.filter_by(role="recruiter").count()
    placement_rate = (placed_students / total_students * 100) if total_students > 0 else 0
    
    return render_template(
        "admin_management.html",
        total_students=total_students,
        placed_students=placed_students,
        total_recruiters=total_recruiters,
        placement_rate=placement_rate
    )


@app.route("/admin/students")
@login_required
@roles_required("admin")
def admin_students():
    department = request.args.get("department")
    min_gpa = request.args.get("min_gpa", type=float)
    skill = request.args.get("skill")

    query = StudentProfile.query.join(User)

    if department:
        query = query.filter(StudentProfile.department == department)
    if min_gpa is not None:
        query = query.filter(StudentProfile.gpa >= min_gpa)
    if skill:
        query = query.filter(StudentProfile.skills.ilike(f"%{skill}%"))

    students = query.all()
    return render_template("admin_students.html", students=students)


@app.route("/admin/recruiters")
@login_required
@roles_required("admin")
def admin_recruiters():
    """Admin view of all recruiters."""
    if database_manager.db_type == "firebase":
        # Firebase implementation
        users_ref = database_manager.user_manager.firebase.get_reference('users').get()
        recruiters = []
        
        if users_ref:
            for user_id, user_data in users_ref.items():
                if user_data.get('role') == 'recruiter':
                    recruiters.append(user_data)
    else:
        # SQLite implementation
        recruiters = User.query.filter_by(role="recruiter").all()
    
    return render_template("admin_recruiters.html", recruiters=recruiters)


@app.route("/admin/analytics")
@login_required
@roles_required("admin")
def admin_analytics():
    """Comprehensive analytics dashboard for admin."""
    if database_manager.db_type == "firebase":
        # Firebase implementation
        profiles_ref = database_manager.profile_manager.firebase.get_reference('student_profiles').get()
        all_profiles = list(profiles_ref.values()) if profiles_ref else []
        
        # Student statistics
        total_students = len(all_profiles)
        placed_students = len([p for p in all_profiles if p.get('placement_status') != 'Not Placed'])
        not_placed_students = total_students - placed_students
        
        # Department-wise statistics
        dept_stats = {}
        if all_profiles:
            for profile in all_profiles:
                dept = profile.get('department', 'Unknown')
                if dept not in dept_stats:
                    dept_stats[dept] = {
                        'count': 0,
                        'avg_gpa': 0.0,
                        'gpa_sum': 0.0
                    }
                dept_stats[dept]['count'] += 1
                gpa = profile.get('gpa', 0.0)
                if gpa:
                    dept_stats[dept]['gpa_sum'] += gpa
            
            # Calculate averages
            for dept, stats in dept_stats.items():
                if stats['count'] > 0:
                    stats['avg_gpa'] = round(stats['gpa_sum'] / stats['count'], 2)
        
        # Recruiter statistics
        users_ref = database_manager.user_manager.firebase.get_reference('users').get()
        recruiters = []
        active_recruiters = 0
        
        if users_ref:
            for user_id, user_data in users_ref.items():
                if user_data.get('role') == 'recruiter':
                    recruiters.append(user_data)
                    # Consider recruiter as active if they have logged in or have recent activity
                    if user_data.get('last_login') or user_data.get('created_at'):
                        active_recruiters += 1
        
        recruiter_success_rate = round((active_recruiters / len(recruiters) * 100), 1) if recruiters else 0
        
        # Recent registrations (last 7 days)
        from datetime import datetime, timedelta
        recent_students = 0  # Firebase doesn't store created_at by default
        
    else:
        # SQLite implementation
        total_students = StudentProfile.query.count()
        placed_students = StudentProfile.query.filter(StudentProfile.placement_status != "Not Placed").count()
        not_placed_students = total_students - placed_students
        
        # Department-wise statistics
        dept_stats = db.session.query(
            StudentProfile.department,
            db.func.count(StudentProfile.id).label('count'),
            db.func.avg(StudentProfile.gpa).label('avg_gpa')
        ).group_by(StudentProfile.department).all()
        
        # Recruiter statistics - fetch all recruiter details
        recruiters = User.query.filter_by(role="recruiter").all()
        total_recruiters = len(recruiters)
        active_recruiters = total_recruiters  # Simplified for SQLite
        recruiter_success_rate = 100.0 if total_recruiters > 0 else 0
        
        # Recent registrations (last 7 days)
        from datetime import datetime, timedelta
        recent_students = User.query.filter(
            User.role == "student",
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
    
    return render_template(
        "admin_analytics.html",
        total_students=total_students,
        placed_students=placed_students,
        not_placed_students=not_placed_students,
        placement_rate=(placed_students/total_students*100) if total_students > 0 else 0,
        dept_stats=dept_stats,
        total_recruiters=len(recruiters) if database_manager.db_type == "firebase" else total_recruiters,
        active_recruiters=active_recruiters,
        recruiter_success_rate=recruiter_success_rate,
        recruiters=recruiters,
        recent_students=recent_students
    )


@app.route("/admin/analytics/export")
@login_required
@roles_required("admin")
def admin_analytics_export():
    """Export analytics data as CSV."""
    import csv
    from io import StringIO
    from flask import Response
    
    # Get analytics data (reuse admin_analytics logic)
    if database_manager.db_type == "firebase":
        profiles_ref = database_manager.profile_manager.firebase.get_reference('student_profiles').get()
        all_profiles = list(profiles_ref.values()) if profiles_ref else []
        
        total_students = len(all_profiles)
        placed_students = len([p for p in all_profiles if p.get('placement_status') != 'Not Placed'])
        
        # Department-wise statistics
        dept_stats = {}
        if all_profiles:
            for profile in all_profiles:
                dept = profile.get('department', 'Unknown')
                if dept not in dept_stats:
                    dept_stats[dept] = {
                        'count': 0,
                        'avg_gpa': 0.0,
                        'gpa_sum': 0.0
                    }
                dept_stats[dept]['count'] += 1
                gpa = profile.get('gpa', 0.0)
                if gpa:
                    dept_stats[dept]['gpa_sum'] += gpa
            
            for dept, stats in dept_stats.items():
                if stats['count'] > 0:
                    stats['avg_gpa'] = round(stats['gpa_sum'] / stats['count'], 2)
    else:
        # SQLite implementation
        total_students = StudentProfile.query.count()
        placed_students = StudentProfile.query.filter(StudentProfile.placement_status != "Not Placed").count()
        
        dept_stats = db.session.query(
            StudentProfile.department,
            db.func.count(StudentProfile.id).label('count'),
            db.func.avg(StudentProfile.gpa).label('avg_gpa')
        ).group_by(StudentProfile.department).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['PyTech Arena Analytics Report'])
    writer.writerow(['Generated on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Overall Statistics
    writer.writerow(['Overall Statistics'])
    writer.writerow(['Total Students', total_students])
    writer.writerow(['Placed Students', placed_students])
    writer.writerow(['Placement Rate (%)', round((placed_students/total_students*100), 1) if total_students > 0 else 0])
    writer.writerow([])
    
    # Department-wise Statistics
    writer.writerow(['Department-wise Statistics'])
    writer.writerow(['Department', 'Total Students', 'Average GPA'])
    
    if database_manager.db_type == "firebase":
        for dept, stats in dept_stats.items():
            writer.writerow([dept, stats['count'], stats['avg_gpa']])
    else:
        for dept, count, avg_gpa in dept_stats:
            writer.writerow([dept, count, round(avg_gpa, 2) if avg_gpa else 0.0])
    
    # Create response
    output.seek(0)
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=analytics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response


@app.route("/admin/student/<int:student_id>/delete", methods=["POST"])
@login_required
@roles_required("admin")
def admin_delete_student(student_id):
    """Delete a student account."""
    profile = StudentProfile.query.get_or_404(student_id)
    user = User.query.get(profile.user_id)
    
    db.session.delete(profile)
    db.session.delete(user)
    db.session.commit()
    
    flash("Student deleted successfully.", "success")
    return redirect(url_for("admin_students"))


@app.route("/admin/recruiter/<recruiter_id>/edit", methods=["POST"])
@login_required
@roles_required("admin")
def admin_edit_recruiter(recruiter_id):
    """Edit a recruiter account."""
    name = request.form.get("name")
    email = request.form.get("email")
    company_name = request.form.get("company_name")
    
    if database_manager.db_type == "firebase":
        # Firebase implementation
        user_ref = database_manager.user_manager.firebase.get_reference('users').child(recruiter_id)
        user_data = user_ref.get()
        
        if not user_data or user_data.get('role') != 'recruiter':
            flash("Recruiter not found.", "danger")
            return redirect(url_for("admin_recruiters"))
        
        # Update recruiter data
        updates = {
            'name': name,
            'email': email,
            'company_name': company_name
        }
        user_ref.update(updates)
    else:
        # SQLite implementation
        user = User.query.get_or_404(recruiter_id)
        
        if user.role != "recruiter":
            flash("Invalid user.", "danger")
            return redirect(url_for("admin_recruiters"))
        
        user.name = name
        user.email = email
        user.company_name = company_name
        db.session.commit()
    
    flash("Recruiter updated successfully.", "success")
    return redirect(url_for("admin_recruiters"))


@app.route("/admin/recruiter/<int:recruiter_id>/delete", methods=["POST"])
@login_required
@roles_required("admin")
def admin_delete_recruiter(recruiter_id):
    """Delete a recruiter account."""
    user = User.query.get_or_404(recruiter_id)
    
    if user.role != "recruiter":
        flash("Invalid user.", "danger")
        return redirect(url_for("admin_recruiters"))
    
    db.session.delete(user)
    db.session.commit()
    
    flash("Recruiter deleted successfully.", "success")
    return redirect(url_for("admin_recruiters"))


@app.route("/admin/recruiters/export")
@login_required
@roles_required("admin")
def admin_export_recruiters():
    """Export recruiters data as CSV."""
    import csv
    from io import StringIO
    from flask import Response
    
    # Get recruiters data
    if database_manager.db_type == "firebase":
        users_ref = database_manager.user_manager.firebase.get_reference('users').get()
        recruiters = []
        if users_ref:
            for user_id, user_data in users_ref.items():
                if user_data.get('role') == 'recruiter':
                    recruiters.append({
                        'id': user_id,
                        'name': user_data.get('name', user_data.get('username', 'N/A')),
                        'email': user_data.get('email', 'N/A'),
                        'company_name': user_data.get('company_name', 'Not specified'),
                        'created_at': user_data.get('created_at', 'N/A'),
                        'last_login': user_data.get('last_login', 'Never')
                    })
    else:
        recruiters_data = User.query.filter_by(role="recruiter").all()
        recruiters = []
        for r in recruiters_data:
            recruiters.append({
                'id': r.id,
                'name': r.name,
                'email': r.email,
                'company_name': getattr(r, 'company_name', 'Not specified'),
                'created_at': r.created_at.strftime('%Y-%m-%d') if r.created_at else 'N/A',
                'last_login': r.last_login.strftime('%Y-%m-%d %H:%M') if getattr(r, 'last_login', None) else 'Never'
            })
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Company', 'Registration Date', 'Last Login'])
    
    for recruiter in recruiters:
        writer.writerow([
            recruiter['id'],
            recruiter['name'],
            recruiter['email'],
            recruiter['company_name'],
            recruiter['created_at'][:10] if recruiter['created_at'] != 'N/A' else 'N/A',
            recruiter['last_login']
        ])
    
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=recruiters_export.csv"}
    )


@app.route("/recruiter/dashboard")
@login_required
@roles_required("recruiter")
def recruiter_dashboard():
    min_gpa = request.args.get("min_gpa", type=float, default=0.0)
    skill = request.args.get("skill")
    department = request.args.get("department")

    query = StudentProfile.query.join(User).filter(StudentProfile.gpa >= min_gpa)
    if skill:
        query = query.filter(StudentProfile.skills.ilike(f"%{skill}%"))
    if department:
        query = query.filter(StudentProfile.department == department)

    students = query.all()
    
    # Get all job applications ordered by most recent
    job_applications = JobApplication.query.order_by(JobApplication.applied_at.desc()).all()
    
    return render_template("recruiter_dashboard.html", students=students, job_applications=job_applications)


@app.route("/student/upload", methods=["GET", "POST"])
@login_required
@roles_required("student")
def student_upload():
    """Handle document uploads for students."""
    user_id = session["user_id"]
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    if request.method == "POST":
        resume = request.files.get("resume")
        photo = request.files.get("photo")
        
        if resume and resume.filename:
            resume_filename = f"resume_{user_id}_{resume.filename}"
            resume.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_filename))
            profile.resume_filename = resume_filename
            flash("Resume uploaded successfully.", "success")
        
        if photo and photo.filename:
            photo_filename = f"photo_{user_id}_{photo.filename}"
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))
            profile.photo_filename = photo_filename
            flash("Photo uploaded successfully.", "success")
        
        db.session.commit()
        return redirect(url_for("student_dashboard"))
    
    return render_template("student_upload.html", profile=profile)


@app.route("/student/status")
@login_required
@roles_required("student")
def student_status():
    """View placement status and opportunities."""
    if database_manager.db_type == "firebase":
        # Firebase implementation
        profile = database_manager.get_student_profile(current_user.id)
        
        # Get student's applications from Firebase
        applications_ref = database_manager.job_manager.firebase.get_reference('job_applications').get()
        opportunities = []
        
        if applications_ref:
            for app_id, app_data in applications_ref.items():
                if app_data.get('user_id') == current_user.id:
                    opportunities.append({
                        "title": app_data.get('job_title', 'Unknown Position'),
                        "type": app_data.get('job_type', 'Full-time'),
                        "location": app_data.get('location', 'Not specified'),
                        "salary": app_data.get('salary', 'Not specified'),
                        "status": app_data.get('status', 'Applied')
                    })
    else:
        # SQLite implementation
        profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
        
        # Mock opportunities data - in real app, fetch from database
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
    
    return render_template("student_status.html", profile=profile, opportunities=opportunities)


@app.route("/student/opportunities")
@login_required
@roles_required("student")
def student_opportunities():
    """View all placement opportunities."""
    opportunities = [
        {
            "id": 1,
            "title": "Software Engineer",
            "company": "TechCorp",
            "type": "Full-time",
            "location": "Remote",
            "salary": "$80,000 - $120,000",
            "description": "Looking for Python developers"
        },
        {
            "id": 2,
            "title": "Frontend Developer",
            "company": "StartupXYZ",
            "type": "Full-time",
            "location": "Hybrid",
            "salary": "$70,000 - $100,000",
            "description": "React and JavaScript expertise needed"
        }
    ]
    return render_template("student_opportunities.html", opportunities=opportunities)


@app.route("/student/apply/<int:opportunity_id>", methods=["POST"])
@login_required
@roles_required("student")
def apply_opportunity(opportunity_id):
    """Apply for a placement opportunity."""
    flash("Application submitted successfully! The placement cell will review your application.", "success")
    return redirect(url_for("student_opportunities"))


@app.route("/recruiter/contact/<int:student_id>", methods=["GET", "POST"])
@login_required
@roles_required("recruiter")
def contact_student(student_id):
    """View student contact details (recruiter function)."""
    profile = StudentProfile.query.get_or_404(student_id)
    user = User.query.get(profile.user_id)
    
    return render_template("student_contact.html", profile=profile, user=user)


@app.route("/recruiter/view-resume/<int:student_id>")
@login_required
@roles_required("recruiter")
def view_resume(student_id):
    """View student resume (recruiter function)."""
    from flask import send_from_directory
    profile = StudentProfile.query.get_or_404(student_id)
    
    if profile.resume_filename:
        # Serve the resume file
        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            profile.resume_filename,
            as_attachment=False
        )
    else:
        flash("This student has not uploaded a resume yet.", "warning")
        return redirect(url_for("recruiter_dashboard"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Separate admin login page."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Use database manager to verify admin credentials (consistent with regular login)
        user = database_manager.verify_password(email, password)
        
        if not user:
            flash("Admin account not found. Please check your credentials.", "danger")
            return redirect(url_for("admin_login"))
        
        # database_manager.verify_password returns dictionary, not User object
        # Check if password matches the stored hash
        if user and 'password_hash' in user:
            from werkzeug.security import check_password_hash
            if not check_password_hash(user['password_hash'], password):
                flash("Invalid password.", "danger")
                return redirect(url_for("admin_login"))
        
        session["user_id"] = user.id
        session["role"] = user.role
        
        flash("Admin logged in successfully.", "success")
        return redirect(url_for("admin_dashboard"))
    
    return render_template("admin_login.html")


@app.cli.command("init-db")
def init_db():
    """Initialize the database and create default data if none exists."""
    db.create_all()
    
    # Create admin user with specific credentials
    if not User.query.filter_by(role="admin").first():
        admin = User(name="Placement Officer", email="placement@jntugv.edu.in", role="admin")
        admin.set_password("Admin@2026")
        db.session.add(admin)
        db.session.commit()
        print("=" * 60)
        print("ADMIN ACCOUNT CREATED")
        print("=" * 60)
        print("Email: placement@jntugv.edu.in")
        print("Password: Admin@2026")
        print("=" * 60)
    else:
        print("Admin already exists.")
    
    # Create sample companies if none exist
    if not Company.query.first():
        companies_data = [
            {
                "name": "Cognizant Technology Solutions",
                "short_name": "Cognizant",
                "description": "Cognizant is an American multinational technology company that provides business consulting, information technology and outsourcing services.",
                "industry": "Information Technology & Consulting",
                "headquarters": "Teaneck, New Jersey, USA (India HQ: Chennai)",
                "employees": "350,000+",
                "website": "www.cognizant.com",
                "logo_letter": "C",
                "gradient": "linear-gradient(135deg, #0033a0 0%, #00b4d8 100%)"
            },
            {
                "name": "Infosys Limited",
                "short_name": "Infosys",
                "description": "Infosys is an Indian multinational information technology company that provides business consulting, information technology and outsourcing services.",
                "industry": "Information Technology Services",
                "headquarters": "Bangalore, Karnataka, India",
                "employees": "300,000+",
                "website": "www.infosys.com",
                "logo_letter": "I",
                "gradient": "linear-gradient(135deg, #007cc2 0%, #00b4d8 100%)"
            },
            {
                "name": "Wipro Technologies",
                "short_name": "Wipro",
                "description": "Wipro is an Indian multinational corporation that provides information technology, consulting and business process services.",
                "industry": "IT Services & Consulting",
                "headquarters": "Bangalore, Karnataka, India",
                "employees": "250,000+",
                "website": "www.wipro.com",
                "logo_letter": "W",
                "gradient": "linear-gradient(135deg, #5e8c31 0%, #7cb342 100%)"
            },
            {
                "name": "Drishya AI Labs",
                "short_name": "Drishya AI",
                "description": "Drishya AI Labs is an innovative artificial intelligence and machine learning company specializing in computer vision, natural language processing, and AI-powered solutions.",
                "industry": "Artificial Intelligence & Machine Learning",
                "headquarters": "Hyderabad, Telangana, India",
                "employees": "500+",
                "website": "www.drishya.ai",
                "logo_letter": "D",
                "gradient": "linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)"
            }
        ]
        
        for company_data in companies_data:
            company = Company(**company_data)
            db.session.add(company)
        
        db.session.commit()
        print("Sample companies created.")
    
    # Create sample job postings if none exist
    if not JobPosting.query.first():
        companies = Company.query.all()
        jobs_data = [
            {
                "company": companies[0],  # Cognizant
                "title": "Software Engineer",
                "description": "Looking for talented software engineers to join our team.",
                "requirements": "B.Tech with 60% aggregate, strong programming skills",
                "location": "Hyderabad",
                "job_type": "Full-time",
                "salary_range": "4.0 - 8.0 LPA",
                "eligibility": "B.Tech/BE (All branches) with 60% aggregate, no active backlogs",
                "application_process": "Online Assessment -> Technical Interview -> HR Interview"
            },
            {
                "company": companies[1],  # Infosys
                "title": "Systems Engineer",
                "description": "Join our team of innovators and problem-solvers.",
                "requirements": "Strong analytical and problem-solving skills",
                "location": "Bangalore",
                "job_type": "Full-time",
                "salary_range": "3.6 - 9.5 LPA",
                "eligibility": "B.Tech/BE (All branches) with 60% aggregate, no active backlogs",
                "application_process": "Online Test -> Technical Interview -> Behavioral Interview"
            },
            {
                "company": companies[2],  # Wipro
                "title": "Project Engineer",
                "description": "Exciting opportunities for fresh graduates.",
                "requirements": "Good communication and technical skills",
                "location": "Chennai",
                "job_type": "Full-time",
                "salary_range": "3.5 - 6.5 LPA",
                "eligibility": "B.Tech/BE (CSE, IT, ECE, EEE) with 60% aggregate",
                "application_process": "Aptitude Test -> Coding Test -> Technical Round -> HR Round"
            },
            {
                "company": companies[3],  # Drishya AI
                "title": "AI Engineer",
                "description": "Work on cutting-edge AI and ML projects.",
                "requirements": "Strong Python and machine learning background",
                "location": "Hyderabad",
                "job_type": "Full-time",
                "salary_range": "6.0 - 15.0 LPA",
                "eligibility": "B.Tech/BE (CSE, IT, ECE) with 65% aggregate, strong in Python and algorithms",
                "application_process": "Online Coding Test -> Technical Interview -> Machine Learning Assessment -> HR Interview"
            }
        ]
        
        for job_data in jobs_data:
            job = JobPosting(
                company=job_data["company"],
                title=job_data["title"],
                description=job_data["description"],
                requirements=job_data["requirements"],
                location=job_data["location"],
                job_type=job_data["job_type"],
                salary_range=job_data["salary_range"],
                eligibility=job_data["eligibility"],
                application_process=job_data["application_process"]
            )
            db.session.add(job)
        
        db.session.commit()
        print("Sample job postings created.")
    
    print("Database initialization complete!")


# Company data
COMPANIES = {
    "cognizant": {
        "name": "Cognizant Technology Solutions",
        "short_name": "Cognizant",
        "logo_letter": "C",
        "gradient": "linear-gradient(135deg, #0033a0 0%, #00b4d8 100%)",
        "description": "Cognizant is an American multinational technology company that provides business consulting, information technology and outsourcing services. It is one of the leading professional services companies in the world.",
        "industry": "Information Technology & Consulting",
        "headquarters": "Teaneck, New Jersey, USA (India HQ: Chennai)",
        "employees": "350,000+",
        "website": "www.cognizant.com",
        "visit_date": "March 15, 2026",
        "visit_time": "9:00 AM - 5:00 PM",
        "venue": "JNTU GV Placement Cell, Main Auditorium",
        "positions": ["Software Engineer", "Programmer Analyst", "Associate", "Senior Associate"],
        "package": "4.0 - 8.0 LPA",
        "eligibility": "B.Tech/BE (All branches) with 60% aggregate, no active backlogs",
        "process": ["Online Assessment", "Technical Interview", "HR Interview"]
    },
    "infosys": {
        "name": "Infosys Limited",
        "short_name": "Infosys",
        "logo_letter": "I",
        "gradient": "linear-gradient(135deg, #007cc2 0%, #00b4d8 100%)",
        "description": "Infosys is an Indian multinational information technology company that provides business consulting, information technology and outsourcing services. It is the second-largest Indian IT company.",
        "industry": "Information Technology Services",
        "headquarters": "Bangalore, Karnataka, India",
        "employees": "300,000+",
        "website": "www.infosys.com",
        "visit_date": "April 2, 2026",
        "visit_time": "10:00 AM - 6:00 PM",
        "venue": "JNTU GV Placement Cell, Seminar Hall 1",
        "positions": ["Systems Engineer", "Digital Specialist", "Power Programmer", "Specialist Programmer"],
        "package": "3.6 - 9.5 LPA",
        "eligibility": "B.Tech/BE (All branches) with 60% aggregate, no active backlogs",
        "process": ["Online Test", "Technical Interview", "Behavioral Interview"]
    },
    "wipro": {
        "name": "Wipro Technologies",
        "short_name": "Wipro",
        "logo_letter": "W",
        "gradient": "linear-gradient(135deg, #5e8c31 0%, #7cb342 100%)",
        "description": "Wipro is an Indian multinational corporation that provides information technology, consulting and business process services. It is one of the leading IT companies in India.",
        "industry": "IT Services & Consulting",
        "headquarters": "Bangalore, Karnataka, India",
        "employees": "250,000+",
        "website": "www.wipro.com",
        "visit_date": "March 28, 2026",
        "visit_time": "9:30 AM - 4:30 PM",
        "venue": "JNTU GV Placement Cell, Conference Hall",
        "positions": ["Project Engineer", "Software Developer", "Test Engineer", "Technical Support"],
        "package": "3.5 - 6.5 LPA",
        "eligibility": "B.Tech/BE (CSE, IT, ECE, EEE) with 60% aggregate",
        "process": ["Aptitude Test", "Coding Test", "Technical Round", "HR Round"]
    },
    "drishya": {
        "name": "Drishya AI Labs",
        "short_name": "Drishya AI",
        "logo_letter": "D",
        "gradient": "linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)",
        "description": "Drishya AI Labs is an innovative artificial intelligence and machine learning company specializing in computer vision, natural language processing, and AI-powered solutions for enterprises.",
        "industry": "Artificial Intelligence & Machine Learning",
        "headquarters": "Hyderabad, Telangana, India",
        "employees": "500+",
        "website": "www.drishya.ai",
        "visit_date": "April 10, 2026",
        "visit_time": "9:00 AM - 6:00 PM",
        "venue": "JNTU GV Placement Cell, Seminar Hall 2",
        "positions": ["AI Engineer", "ML Engineer", "Data Scientist", "Python Developer"],
        "package": "6.0 - 15.0 LPA",
        "eligibility": "B.Tech/BE (CSE, IT, ECE) with 65% aggregate, strong in Python and algorithms",
        "process": ["Online Coding Test", "Technical Interview", "Machine Learning Assessment", "HR Interview"]
    }
}


@app.route("/company/<company_id>")
def company_details(company_id):
    company = COMPANIES.get(company_id)
    if not company:
        flash("Company not found!", "error")
        return redirect(url_for("index"))
    return render_template("company_details.html", company=company)


@app.route("/apply-job", methods=["POST"])
@login_required
def apply_job():
    if current_user.role != "student":
        flash("Only students can apply for jobs!", "error")
        return redirect(url_for("index"))
    
    job_id = request.form.get("job_id")
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    department = request.form.get("department")
    cgpa = request.form.get("cgpa")
    skills = request.form.get("skills")
    cover_letter = request.form.get("cover_letter")
    
    # Get company and job details based on job_id
    company_data = {
        "tcs": {"name": "Tata Consultancy Services", "title": "Software Engineer"},
        "infosys": {"name": "Infosys Limited", "title": "Systems Engineer"},
        "wipro": {"name": "Wipro Technologies", "title": "Project Engineer"},
        "accenture": {"name": "Accenture India", "title": "Associate Software Engineer"}
    }
    
    job_info = company_data.get(job_id, {"name": "Unknown Company", "title": "Unknown Position"})
    
    # Create new job application
    application = JobApplication(
        student_id=current_user.id,
        job_id=job_id,
        company_name=job_info["name"],
        job_title=job_info["title"],
        full_name=full_name,
        email=email,
        phone=phone,
        department=department,
        cgpa=cgpa,
        skills=skills,
        cover_letter=cover_letter,
        status="Pending"
    )
    
    db.session.add(application)
    db.session.commit()
    
    flash(f"Your application for {job_info['name']} has been submitted successfully! We will review your application and get back to you soon.", "success")
    return redirect(url_for("student_dashboard"))


@app.route("/update-application-status/<int:application_id>", methods=["POST"])
@login_required
@roles_required("recruiter")
def update_application_status(application_id):
    application = JobApplication.query.get_or_404(application_id)
    new_status = request.form.get("status")
    
    if new_status in ["Pending", "Reviewed", "Shortlisted", "Rejected"]:
        application.status = new_status
        db.session.commit()
        flash(f"Application status updated to {new_status} successfully!", "success")
    else:
        flash("Invalid status!", "error")
    
    return redirect(url_for("recruiter_dashboard"))


# Company Management Routes
@app.route("/admin/companies")
@login_required
@roles_required("admin")
def admin_companies():
    """Manage companies."""
    companies = Company.query.all()
    return render_template("admin_companies.html", companies=companies)


@app.route("/admin/companies/add", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def admin_add_company():
    """Add a new company."""
    if request.method == "POST":
        company = Company(
            name=request.form.get("name"),
            short_name=request.form.get("short_name"),
            description=request.form.get("description"),
            industry=request.form.get("industry"),
            headquarters=request.form.get("headquarters"),
            employees=request.form.get("employees"),
            website=request.form.get("website"),
            logo_letter=request.form.get("logo_letter", "C"),
            gradient=request.form.get("gradient", "linear-gradient(135deg, #0033a0 0%, #00b4d8 100%)")
        )
        db.session.add(company)
        db.session.commit()
        flash("Company added successfully!", "success")
        return redirect(url_for("admin_companies"))
    
    return render_template("admin_company_form.html", company=None)


@app.route("/admin/companies/<int:company_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def admin_edit_company(company_id):
    """Edit a company."""
    company = Company.query.get_or_404(company_id)
    
    if request.method == "POST":
        company.name = request.form.get("name")
        company.short_name = request.form.get("short_name")
        company.description = request.form.get("description")
        company.industry = request.form.get("industry")
        company.headquarters = request.form.get("headquarters")
        company.employees = request.form.get("employees")
        company.website = request.form.get("website")
        company.logo_letter = request.form.get("logo_letter", "C")
        company.gradient = request.form.get("gradient", "linear-gradient(135deg, #0033a0 0%, #00b4d8 100%)")
        
        db.session.commit()
        flash("Company updated successfully!", "success")
        return redirect(url_for("admin_companies"))
    
    return render_template("admin_company_form.html", company=company)


@app.route("/admin/companies/<int:company_id>/delete", methods=["POST"])
@login_required
@roles_required("admin")
def admin_delete_company(company_id):
    """Delete a company."""
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    flash("Company deleted successfully!", "success")
    return redirect(url_for("admin_companies"))


# Job Posting Management
@app.route("/admin/jobs")
@login_required
@roles_required("admin")
def admin_jobs():
    """Manage job postings."""
    jobs = JobPosting.query.join(Company).all()
    companies = Company.query.all()
    return render_template("admin_jobs.html", jobs=jobs, companies=companies)


@app.route("/admin/jobs/add", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def admin_add_job():
    """Add a new job posting."""
    if request.method == "POST":
        job = JobPosting(
            company_id=request.form.get("company_id"),
            title=request.form.get("title"),
            description=request.form.get("description"),
            requirements=request.form.get("requirements"),
            location=request.form.get("location"),
            job_type=request.form.get("job_type"),
            salary_range=request.form.get("salary_range"),
            eligibility=request.form.get("eligibility"),
            application_process=request.form.get("application_process"),
            visit_date=datetime.strptime(request.form.get("visit_date"), "%Y-%m-%d") if request.form.get("visit_date") else None,
            visit_time=request.form.get("visit_time"),
            venue=request.form.get("venue"),
            deadline=datetime.strptime(request.form.get("deadline"), "%Y-%m-%d") if request.form.get("deadline") else None
        )
        db.session.add(job)
        db.session.commit()
        flash("Job posting added successfully!", "success")
        return redirect(url_for("admin_jobs"))
    
    companies = Company.query.filter_by(is_active=True).all()
    return render_template("admin_job_form.html", job=None, companies=companies)


@app.route("/admin/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def admin_edit_job(job_id):
    """Edit a job posting."""
    job = JobPosting.query.get_or_404(job_id)
    
    if request.method == "POST":
        job.company_id = request.form.get("company_id")
        job.title = request.form.get("title")
        job.description = request.form.get("description")
        job.requirements = request.form.get("requirements")
        job.location = request.form.get("location")
        job.job_type = request.form.get("job_type")
        job.salary_range = request.form.get("salary_range")
        job.eligibility = request.form.get("eligibility")
        job.application_process = request.form.get("application_process")
        job.visit_date = datetime.strptime(request.form.get("visit_date"), "%Y-%m-%d") if request.form.get("visit_date") else None
        job.visit_time = request.form.get("visit_time")
        job.venue = request.form.get("venue")
        job.deadline = datetime.strptime(request.form.get("deadline"), "%Y-%m-%d") if request.form.get("deadline") else None
        
        db.session.commit()
        flash("Job posting updated successfully!", "success")
        return redirect(url_for("admin_jobs"))
    
    companies = Company.query.filter_by(is_active=True).all()
    return render_template("admin_job_form.html", job=job, companies=companies)


@app.route("/admin/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
@roles_required("admin")
def admin_delete_job(job_id):
    """Delete a job posting."""
    job = JobPosting.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Job posting deleted successfully!", "success")
    return redirect(url_for("admin_jobs"))


# Notification System
@app.route("/notifications")
@login_required
def notifications():
    """View user notifications."""
    user_id = session["user_id"]
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    
    # Mark notifications as read
    for notification in notifications:
        if not notification.is_read:
            notification.is_read = True
    
    db.session.commit()
    return render_template("notifications.html", notifications=notifications)


@app.route("/api/notifications/mark-read/<int:notification_id>", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read via API."""
    user_id = session["user_id"]
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Notification not found"}), 404


# Student Job Applications
@app.route("/student/jobs")
@login_required
@roles_required("student")
def student_jobs():
    """View available job postings."""
    user_id = session["user_id"]
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    # Get active job postings
    jobs = JobPosting.query.filter_by(is_active=True).join(Company).all()
    
    # Filter jobs based on student profile
    eligible_jobs = []
    for job in jobs:
        if profile.gpa >= 6.0:  # Basic GPA requirement
            eligible_jobs.append(job)
    
    # Get student's applications
    applications = JobApplication.query.filter_by(student_id=user_id).all()
    applied_job_ids = [app.job_id for app in applications]
    
    return render_template("student_jobs.html", jobs=eligible_jobs, applied_job_ids=applied_job_ids)


@app.route("/student/apply-job/<int:job_id>", methods=["GET", "POST"])
@login_required
@roles_required("student")
def student_apply_job(job_id):
    """Apply for a specific job."""
    user_id = session["user_id"]
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    job = JobPosting.query.get_or_404(job_id)
    
    # Check if already applied
    existing_application = JobApplication.query.filter_by(
        student_id=user_id, 
        job_posting_id=job_id
    ).first()
    
    if existing_application:
        flash("You have already applied for this job!", "warning")
        return redirect(url_for("student_jobs"))
    
    if request.method == "POST":
        application = JobApplication(
            student_id=user_id,
            job_posting_id=job_id,  # Use the foreign key
            job_id=str(job_id),  # Keep for backward compatibility
            company_name=job.company.name,
            job_title=job.title,
            full_name=request.form.get("full_name", current_user.name),
            email=request.form.get("email", current_user.email),
            phone=request.form.get("phone", profile.phone or ""),
            department=profile.department,
            cgpa=str(profile.gpa),
            skills=profile.skills,
            cover_letter=request.form.get("cover_letter"),
            status="Pending"
        )
        
        db.session.add(application)
        db.session.commit()
        
        # Create notification for student
        create_notification(
            user_id,
            "Application Submitted",
            f"Your application for {job.title} at {job.company.name} has been submitted successfully.",
            "success"
        )
        
        flash("Application submitted successfully!", "success")
        return redirect(url_for("student_jobs"))
    
    return render_template("student_job_application.html", job=job, profile=profile)


@app.route("/student/applications")
@login_required
@roles_required("student")
def student_applications():
    """View student's job applications."""
    user_id = session["user_id"]
    applications = JobApplication.query.filter_by(student_id=user_id).order_by(JobApplication.applied_at.desc()).all()
    return render_template("student_applications.html", applications=applications)


# Analytics and Reporting
@app.route("/admin/reports")
@login_required
@roles_required("admin")
def admin_reports():
    """Generate placement reports."""
    report_data = generate_placement_report()
    return render_template("admin_reports.html", report=report_data)


@app.route("/admin/reports/export/csv")
@login_required
@roles_required("admin")
def export_csv_report():
    """Export placement data as CSV file."""
    import csv
    from io import StringIO
    
    # Get student data
    students = db.session.query(
        User.name, User.email, StudentProfile.department, 
        StudentProfile.gpa, StudentProfile.placement_status,
        StudentProfile.skills
    ).join(StudentProfile).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Email', 'Department', 'GPA', 'Placement Status', 'Skills'])
    
    # Write data
    for student in students:
        writer.writerow([
            student.name, student.email, student.department,
            student.gpa, student.placement_status, student.skills or ""
        ])
    
    # Create response
    output.seek(0)
    return app.response_class(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=placement_report.csv'}
    )


@app.route("/api/analytics/dashboard")
@login_required
@roles_required("admin")
def api_analytics_dashboard():
    """API endpoint for dashboard analytics."""
    report_data = generate_placement_report()
    
    # Prepare chart data
    dept_labels = [dept.department for dept in report_data['dept_stats']]
    dept_placed = [dept.placed for dept in report_data['dept_stats']]
    dept_total = [dept.total for dept in report_data['dept_stats']]
    
    return jsonify({
        'summary': {
            'total_students': report_data['total_students'],
            'placed_students': report_data['placed_students'],
            'placement_rate': report_data['placement_rate']
        },
        'department_chart': {
            'labels': dept_labels,
            'placed': dept_placed,
            'total': dept_total
        },
        'company_stats': [
            {
                'name': company.company_name,
                'applications': company.applications,
                'shortlisted': company.shortlisted
            }
            for company in report_data['company_stats']
        ]
    })


# Placement Drive Management
@app.route("/admin/drives")
@login_required
@roles_required("admin")
def admin_drives():
    """Manage placement drives."""
    drives = PlacementDrive.query.all()
    return render_template("admin_drives.html", drives=drives)


@app.route("/admin/drives/add", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def admin_add_drive():
    """Add a new placement drive."""
    if request.method == "POST":
        drive = PlacementDrive(
            name=request.form.get("name"),
            description=request.form.get("description"),
            start_date=datetime.strptime(request.form.get("start_date"), "%Y-%m-%d"),
            end_date=datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
        )
        db.session.add(drive)
        db.session.commit()
        
        # Add participating companies
        company_ids = request.form.getlist("company_ids")
        for company_id in company_ids:
            company = Company.query.get(company_id)
            if company:
                drive.participating_companies.append(company)
        
        db.session.commit()
        flash("Placement drive added successfully!", "success")
        return redirect(url_for("admin_drives"))
    
    companies = Company.query.filter_by(is_active=True).all()
    return render_template("admin_drive_form.html", drive=None, companies=companies)


@app.route("/admin/drives/<int:drive_id>/delete", methods=["POST"])
@login_required
@roles_required("admin")
def admin_delete_drive(drive_id):
    """Delete a placement drive."""
    drive = PlacementDrive.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    flash("Placement drive deleted successfully!", "success")
    return redirect(url_for("admin_drives"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

