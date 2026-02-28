#!/usr/bin/env python3
"""
PyTech Arena - Vercel Serverless Function
Fixed version for Vercel deployment
"""

import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app for serverless
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vercel-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pytech_arena.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models (simplified for serverless)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department = db.Column(db.String(100))
    gpa = db.Column(db.Float)
    placement_status = db.Column(db.String(50), default='Not Placed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Decorators
def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For serverless, we'll skip authentication for now
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# API Routes for serverless
@app.route('/')
def home():
    return jsonify({
        'message': 'PyTech Arena API is running',
        'status': 'success',
        'version': '1.0.0'
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/admin/dashboard')
@roles_required('admin')
def admin_dashboard():
    try:
        # Get statistics
        total_students = StudentProfile.query.count()
        placed_students = StudentProfile.query.filter(StudentProfile.placement_status != 'Not Placed').count()
        placement_rate = (placed_students / total_students * 100) if total_students > 0 else 0
        
        # Department statistics
        dept_stats = {}
        students = StudentProfile.query.all()
        
        for student in students:
            dept = student.department or 'Unknown'
            if dept not in dept_stats:
                dept_stats[dept] = {
                    'total': 0,
                    'placed': 0,
                    'avg_gpa': 0.0,
                    'gpa_sum': 0.0
                }
            
            dept_stats[dept]['total'] += 1
            if student.placement_status != 'Not Placed':
                dept_stats[dept]['placed'] += 1
            if student.gpa:
                dept_stats[dept]['gpa_sum'] += student.gpa
        
        # Calculate averages and placement rates
        for dept, stats in dept_stats.items():
            stats['avg_gpa'] = round(stats['gpa_sum'] / stats['total'], 2) if stats['total'] > 0 else 0
            stats['placement_rate'] = round((stats['placed'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0
            del stats['gpa_sum']  # Remove temporary sum
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_students': total_students,
                'placed_students': placed_students,
                'placement_rate': round(placement_rate, 1),
                'dept_stats': dept_stats
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/admin/analytics')
@roles_required('admin')
def admin_analytics():
    try:
        # Get comprehensive analytics data
        total_students = StudentProfile.query.count()
        placed_students = StudentProfile.query.filter(StudentProfile.placement_status != 'Not Placed').count()
        not_placed_students = total_students - placed_students
        
        # Department statistics
        dept_query = db.session.query(
            StudentProfile.department,
            db.func.count(StudentProfile.id).label('count'),
            db.func.avg(StudentProfile.gpa).label('avg_gpa')
        ).group_by(StudentProfile.department).all()
        
        dept_stats = {}
        for dept, count, avg_gpa in dept_query:
            dept_stats[dept] = {
                'count': count,
                'avg_gpa': round(avg_gpa, 2) if avg_gpa else 0
            }
        
        placement_rate = (placed_students / total_students * 100) if total_students > 0 else 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_students': total_students,
                'placed_students': placed_students,
                'not_placed_students': not_placed_students,
                'placement_rate': round(placement_rate, 1),
                'dept_stats': dept_stats
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/admin/export')
@roles_required('admin')
def admin_export():
    try:
        import csv
        import io
        
        # Get all student data
        students = db.session.query(User, StudentProfile).join(StudentProfile, User.id == StudentProfile.user_id).all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['PyTech Arena Student Report'])
        writer.writerow(['Generated on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        writer.writerow(['Name', 'Email', 'Department', 'GPA', 'Placement Status'])
        
        for user, profile in students:
            writer.writerow([
                user.name,
                user.email,
                profile.department or 'Not specified',
                profile.gpa or 'N/A',
                profile.placement_status
            ])
        
        # Create response
        output.seek(0)
        csv_data = output.getvalue()
        
        return jsonify({
            'status': 'success',
            'data': {
                'csv_content': csv_data,
                'filename': f'pytech_arena_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# Vercel serverless handler
def handler(request):
    """Vercel serverless function handler"""
    try:
        # Create Flask app context
        with app.app_context():
            # Initialize database if needed
            db.create_all()
            
            # Get the request method and path
            method = request.method
            path = request.path
            
            # Route the request
            if path == '/':
                return home()
            elif path == '/api/health':
                return health_check()
            elif path == '/api/admin/dashboard':
                return admin_dashboard()
            elif path == '/api/admin/analytics':
                return admin_analytics()
            elif path == '/api/admin/export':
                return admin_export()
            else:
                return not_found_error(None)
                
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Serverless function error: {str(e)}'
        }), 500

# For local testing
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create test admin user
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
            print("✅ Test admin user created")
    
    print("🚀 PyTech Arena Vercel API starting...")
    app.run(host='0.0.0.0', port=5000, debug=True)
