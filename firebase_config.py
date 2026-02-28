"""
Firebase configuration and initialization
Supports both Firestore and Realtime Database
"""

import os
import json
from firebase_admin import credentials

# Import both database managers
try:
    from firebase_db import FirebaseManager, FirebaseUserManager, FirebaseStudentProfileManager, FirebaseJobManager, FirebaseNotificationManager
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

try:
    from firebase_realtime_db import FirebaseRealtimeManager, FirebaseRealtimeUserManager, FirebaseRealtimeStudentProfileManager, FirebaseRealtimeJobManager, FirebaseRealtimeNotificationManager
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False


def get_firebase_credentials():
    """Get Firebase credentials from environment variables."""
    firebase_config = {
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
    }
    
    # Check if we have valid Firebase configuration
    if not firebase_config["project_id"] or not firebase_config["private_key"]:
        return None
    
    return firebase_config


def initialize_firebase():
    """Initialize Firebase and return managers."""
    try:
        firebase_config = get_firebase_credentials()
        if firebase_config:
            # Check if we have a Realtime Database URL
            database_url = os.getenv("FIREBASE_DATABASE_URL")
            
            if database_url and "rtdb.firebaseio.com" in database_url:
                # Use Realtime Database
                if REALTIME_AVAILABLE:
                    realtime_manager = FirebaseRealtimeManager()
                    
                    # Create managers
                    user_manager = FirebaseRealtimeUserManager(realtime_manager)
                    profile_manager = FirebaseRealtimeStudentProfileManager(realtime_manager)
                    job_manager = FirebaseRealtimeJobManager(realtime_manager)
                    notification_manager = FirebaseRealtimeNotificationManager(realtime_manager)
                    
                    print("✅ Firebase Realtime Database initialized")
                    return {
                        'firebase_manager': realtime_manager,
                        'user_manager': user_manager,
                        'profile_manager': profile_manager,
                        'job_manager': job_manager,
                        'notification_manager': notification_manager,
                        'database_type': 'realtime'
                    }
                else:
                    print("❌ Firebase Realtime Database modules not available")
                    return None
            else:
                # Use Firestore
                if FIRESTORE_AVAILABLE:
                    firebase_manager = FirebaseManager()
                    
                    # Create managers
                    user_manager = FirebaseUserManager(firebase_manager)
                    profile_manager = FirebaseStudentProfileManager(firebase_manager)
                    job_manager = FirebaseJobManager(firebase_manager)
                    notification_manager = FirebaseNotificationManager(firebase_manager)
                    
                    print("✅ Firebase Firestore initialized")
                    return {
                        'firebase_manager': firebase_manager,
                        'user_manager': user_manager,
                        'profile_manager': profile_manager,
                        'job_manager': job_manager,
                        'notification_manager': notification_manager,
                        'database_type': 'firestore'
                    }
                else:
                    print("❌ Firebase Firestore modules not available")
                    return None
        else:
            print("⚠️ Firebase configuration not found, using SQLite")
            return None
            
    except Exception as e:
        print(f"❌ Firebase initialization failed: {str(e)}")
        return None


def create_firebase_credentials_file():
    """Create a Firebase credentials file from environment variables."""
    firebase_config = get_firebase_credentials()
    if firebase_config:
        with open('firebase-credentials.json', 'w') as f:
            json.dump(firebase_config, f, indent=2)
        print("✅ Firebase credentials file created")
        return True
    else:
        print("❌ Firebase configuration not found in environment variables")
        return False
