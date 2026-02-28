"""
Database Abstraction Layer for PyTech Arena
Supports both SQLite (SQLAlchemy) and Firebase Firestore
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import os


class DatabaseManager:
    """Abstract base class for database operations."""
    
    def __init__(self, db_type: str):
        self.db_type = db_type
    
    def create_user(self, name: str, email: str, password: str, role: str = "student") -> str:
        """Create a new user."""
        raise NotImplementedError
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        raise NotImplementedError
    
    def verify_password(self, email: str, password: str) -> Optional[Dict]:
        """Verify user password."""
        raise NotImplementedError
    
    def create_student_profile(self, user_id: str, profile_data: Dict) -> str:
        """Create student profile."""
        raise NotImplementedError
    
    def get_student_profile(self, user_id: str) -> Optional[Dict]:
        """Get student profile by user ID."""
        raise NotImplementedError
    
    def update_student_profile(self, profile_id: str, data: Dict) -> bool:
        """Update student profile."""
        raise NotImplementedError
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all active job postings."""
        raise NotImplementedError
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """Get job by ID."""
        raise NotImplementedError
    
    def create_job_application(self, application_data: Dict) -> str:
        """Create job application."""
        raise NotImplementedError
    
    def get_user_applications(self, user_id: str) -> List[Dict]:
        """Get applications for a user."""
        raise NotImplementedError
    
    def create_notification(self, user_id: str, title: str, message: str, 
                          notification_type: str = "info") -> str:
        """Create notification."""
        raise NotImplementedError
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict]:
        """Get notifications for a user."""
        raise NotImplementedError


class SQLiteDatabaseManager(DatabaseManager):
    """SQLite database manager using SQLAlchemy."""
    
    def __init__(self, db, models):
        super().__init__("sqlite")
        self.db = db
        self.User = models['User']
        self.StudentProfile = models['StudentProfile']
        self.JobPosting = models['JobPosting']
        self.JobApplication = models['JobApplication']
        self.Notification = models['Notification']
    
    def create_user(self, name: str, email: str, password: str, role: str = "student") -> str:
        """Create a new user in SQLite."""
        user = self.User(name=name, email=email, role=role)
        user.set_password(password)
        self.db.session.add(user)
        self.db.session.flush()  # Get the user ID
        
        # Create profile for students
        if role == "student":
            profile = self.StudentProfile(
                user_id=user.id,
                department="",
                gpa=0.0,
            )
            self.db.session.add(profile)
        
        self.db.session.commit()
        return str(user.id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email from SQLite."""
        user = self.User.query.filter_by(email=email).first()
        if user:
            return {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'password_hash': user.password_hash
            }
        return None
    
    def verify_password(self, email: str, password: str) -> Optional[Dict]:
        """Verify user password in SQLite."""
        user = self.User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        return None
    
    def create_student_profile(self, user_id: str, profile_data: Dict) -> str:
        """Create student profile in SQLite."""
        profile = self.StudentProfile(user_id=int(user_id), **profile_data)
        self.db.session.add(profile)
        self.db.session.commit()
        return str(profile.id)
    
    def get_student_profile(self, user_id: str) -> Optional[Dict]:
        """Get student profile from SQLite."""
        profile = self.StudentProfile.query.filter_by(user_id=int(user_id)).first()
        if profile:
            return {
                'id': str(profile.id),
                'user_id': str(profile.user_id),
                'department': profile.department,
                'gpa': profile.gpa,
                'skills': profile.skills,
                'internships': profile.internships,
                'projects': profile.projects,
                'certifications': profile.certifications,
                'career_preferences': profile.career_preferences,
                'resume_filename': profile.resume_filename,
                'photo_filename': profile.photo_filename,
                'placement_status': profile.placement_status,
                'phone': profile.phone,
                'linkedin': profile.linkedin,
                'github': profile.github,
                'portfolio': profile.portfolio
            }
        return None
    
    def update_student_profile(self, profile_id: str, data: Dict) -> bool:
        """Update student profile in SQLite."""
        profile = self.StudentProfile.query.get(int(profile_id))
        if profile:
            for key, value in data.items():
                setattr(profile, key, value)
            self.db.session.commit()
            return True
        return False
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all active job postings from SQLite."""
        jobs = self.JobPosting.query.filter_by(is_active=True).all()
        return [{
            'id': str(job.id),
            'title': job.title,
            'description': job.description,
            'requirements': job.requirements,
            'location': job.location,
            'job_type': job.job_type,
            'salary_range': job.salary_range,
            'eligibility': job.eligibility,
            'application_process': job.application_process,
            'visit_date': job.visit_date.isoformat() if job.visit_date else None,
            'visit_time': job.visit_time,
            'venue': job.venue,
            'deadline': job.deadline.isoformat() if job.deadline else None,
            'company_id': str(job.company_id),
            'company': {
                'name': job.company.name,
                'short_name': job.company.short_name,
                'description': job.company.description
            }
        } for job in jobs]
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """Get job by ID from SQLite."""
        job = self.JobPosting.query.get(int(job_id))
        if job:
            return {
                'id': str(job.id),
                'title': job.title,
                'description': job.description,
                'requirements': job.requirements,
                'location': job.location,
                'job_type': job.job_type,
                'salary_range': job.salary_range,
                'eligibility': job.eligibility,
                'application_process': job.application_process,
                'visit_date': job.visit_date.isoformat() if job.visit_date else None,
                'visit_time': job.visit_time,
                'venue': job.venue,
                'deadline': job.deadline.isoformat() if job.deadline else None,
                'company_id': str(job.company_id),
                'company': {
                    'name': job.company.name,
                    'short_name': job.company.short_name,
                    'description': job.company.description
                }
            }
        return None
    
    def create_job_application(self, application_data: Dict) -> str:
        """Create job application in SQLite."""
        application = self.JobApplication(**application_data)
        self.db.session.add(application)
        self.db.session.commit()
        return str(application.id)
    
    def get_user_applications(self, user_id: str) -> List[Dict]:
        """Get applications for a user from SQLite."""
        applications = self.JobApplication.query.filter_by(student_id=int(user_id)).all()
        return [{
            'id': str(app.id),
            'job_id': str(app.job_id),
            'company_name': app.company_name,
            'job_title': app.job_title,
            'status': app.status,
            'applied_at': app.applied_at.isoformat()
        } for app in applications]
    
    def create_notification(self, user_id: str, title: str, message: str, 
                          notification_type: str = "info") -> str:
        """Create notification in SQLite."""
        notification = self.Notification(
            user_id=int(user_id),
            title=title,
            message=message,
            type=notification_type
        )
        self.db.session.add(notification)
        self.db.session.commit()
        return str(notification.id)
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict]:
        """Get notifications for a user from SQLite."""
        query = self.Notification.query.filter_by(user_id=int(user_id))
        if unread_only:
            query = query.filter_by(is_read=False)
        notifications = query.order_by(self.Notification.created_at.desc()).all()
        return [{
            'id': str(notif.id),
            'title': notif.title,
            'message': notif.message,
            'type': notif.type,
            'is_read': notif.is_read,
            'created_at': notif.created_at.isoformat()
        } for notif in notifications]


class FirebaseDatabaseManager(DatabaseManager):
    """Firebase database manager using Firestore or Realtime Database."""
    
    def __init__(self, firebase_managers):
        super().__init__("firebase")
        self.database_type = firebase_managers.get('database_type', 'firestore')
        
        if self.database_type == 'realtime':
            self.user_manager = firebase_managers['user_manager']
            self.profile_manager = firebase_managers['profile_manager']
            self.job_manager = firebase_managers['job_manager']
            self.notification_manager = firebase_managers['notification_manager']
        else:
            # Firestore managers
            self.user_manager = firebase_managers['user_manager']
            self.profile_manager = firebase_managers['profile_manager']
            self.job_manager = firebase_managers['job_manager']
            self.notification_manager = firebase_managers['notification_manager']
    
    def create_user(self, name: str, email: str, password: str, role: str = "student") -> str:
        """Create a new user in Firebase."""
        return self.user_manager.create_user(name, email, password, role)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email from Firebase."""
        return self.user_manager.get_user_by_email(email)
    
    def verify_password(self, email: str, password: str) -> Optional[Dict]:
        """Verify user password in Firebase."""
        return self.user_manager.verify_password(email, password)
    
    def create_student_profile(self, user_id: str, profile_data: Dict) -> str:
        """Create student profile in Firebase."""
        return self.profile_manager.create_profile(user_id, profile_data)
    
    def get_student_profile(self, user_id: str) -> Optional[Dict]:
        """Get student profile from Firebase."""
        return self.profile_manager.get_profile_by_user_id(user_id)
    
    def update_student_profile(self, profile_id: str, data: Dict) -> bool:
        """Update student profile in Firebase."""
        return self.profile_manager.update_profile(profile_id, data)
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all active job postings from Firebase."""
        return self.job_manager.get_active_jobs()
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict]:
        """Get job by ID from Firebase."""
        return self.job_manager.get_job_by_id(job_id)
    
    def create_job_application(self, application_data: Dict) -> str:
        """Create job application in Firebase."""
        return self.job_manager.create_application(application_data)
    
    def get_user_applications(self, user_id: str) -> List[Dict]:
        """Get applications for a user from Firebase."""
        return self.job_manager.get_user_applications(user_id)
    
    def create_notification(self, user_id: str, title: str, message: str, 
                          notification_type: str = "info") -> str:
        """Create notification in Firebase."""
        return self.notification_manager.create_notification(user_id, title, message, notification_type)
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict]:
        """Get notifications for a user from Firebase."""
        return self.notification_manager.get_user_notifications(user_id, unread_only)


def get_database_manager(database_type: str, db=None, models=None, firebase_managers=None):
    """Factory function to get the appropriate database manager."""
    if database_type == "firebase" and firebase_managers:
        return FirebaseDatabaseManager(firebase_managers)
    else:
        return SQLiteDatabaseManager(db, models)
