#!/usr/bin/env python3
"""
Add test recruiter accounts to fix login issues
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def add_test_recruiters():
    """Add test recruiter accounts to database"""
    
    print("🔧 Adding Test Recruiter Accounts")
    print("=" * 50)
    
    try:
        with app.app_context():
            # Clear existing recruiters (optional - comment out if you want to keep existing)
            existing_recruiters = User.query.filter_by(role='recruiter').all()
            if existing_recruiters:
                print(f"🗑️  Found {len(existing_recruiters)} existing recruiters")
                print("   💡 Keeping existing recruiters (comment out clear() below if needed)")
            
            # Add new test recruiters
            test_recruiters = [
                {
                    'name': 'TechCorp Recruiter',
                    'email': 'techcorp@pytecharena.com',
                    'password_hash': generate_password_hash('Recruiter@2026'),
                    'role': 'recruiter',
                    'company_name': 'Tech Corporation'
                },
                {
                    'name': 'StartupXYZ Recruiter',
                    'email': 'startupxyz@pytecharena.com', 
                    'password_hash': generate_password_hash('Recruiter@2026'),
                    'role': 'recruiter',
                    'company_name': 'StartupXYZ Technologies'
                },
                {
                    'name': 'Innovation Labs Recruiter',
                    'email': 'innovation@pytecharena.com',
                    'password_hash': generate_password_hash('Recruiter@2026'),
                    'role': 'recruiter',
                    'company_name': 'Innovation Labs'
                }
            ]
            
            # Optional: Clear existing recruiters
            # User.query.filter_by(role='recruiter').delete()
            # db.session.commit()
            
            for recruiter_data in test_recruiters:
                recruiter = User(**recruiter_data)
                db.session.add(recruiter)
                print(f"   ✅ Added: {recruiter_data['name']} ({recruiter_data['email']})")
            
            db.session.commit()
            
            print(f"\n✅ Successfully added {len(test_recruiters)} test recruiters")
            print("\n📋 Test Login Credentials:")
            for i, recruiter in enumerate(test_recruiters, 1):
                print(f"   {i}. {recruiter['email']} / Recruiter@2026")
            
            print("\n🌐 Now test recruiter login:")
            print("   URL: http://127.0.0.1:5000/login")
            print("   Use any of the credentials above")
            
    except Exception as e:
        print(f"❌ Error adding recruiters: {str(e)}")
        return False
    
    return True

def verify_recruiter_login():
    """Test recruiter login functionality"""
    
    print("\n🧪 Testing Recruiter Login")
    print("=" * 30)
    
    try:
        with app.app_context():
            from database_manager import database_manager
            
            # Test login with first recruiter
            test_email = 'techcorp@pytecharena.com'
            test_password = 'Recruiter@2026'
            
            print(f"🔍 Testing login with: {test_email}")
            
            result = database_manager.verify_password(test_email, test_password)
            
            if result:
                print(f"   ✅ Login SUCCESS!")
                print(f"   👤 User: {result['name']}")
                print(f"   📧 Role: {result['role']}")
                print(f"   🏢 Should redirect to: recruiter_dashboard")
            else:
                print(f"   ❌ Login FAILED!")
                print(f"   🔍 Check verify_password function")
            
    except Exception as e:
        print(f"❌ Error testing login: {str(e)}")
    
    print("\n" + "=" * 30)
    print("🎯 Next Steps:")
    print("1. Start the application: python app.py")
    print("2. Go to: http://127.0.0.1:5000/login")
    print("3. Use test recruiter credentials")
    print("4. Verify dashboard access")

if __name__ == "__main__":
    print("🚀 PyTech Arena - Recruiter Login Fix")
    print("=" * 50)
    
    success = add_test_recruiters()
    
    if success:
        verify_recruiter_login()
    
    print("\n🎉 Recruiter login fix completed!")
    print("📖 See RECRUITER_LOGIN_SOLVED.md for details")
