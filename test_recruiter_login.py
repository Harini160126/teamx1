#!/usr/bin/env python3
"""
Quick fix for recruiter login issues
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app import app, db
from models import User

def test_recruiter_login():
    """Test recruiter login functionality"""
    
    print("🔍 Testing Recruiter Login Functionality")
    print("=" * 50)
    
    # Test database connection
    try:
        with app.app_context():
            # Check if we have recruiter users in database
            recruiters = User.query.filter_by(role='recruiter').all()
            print(f"📊 Found {len(recruiters)} recruiters in database")
            
            for recruiter in recruiters:
                print(f"   👤 {recruiter.name} ({recruiter.email})")
            
            # Test verify_password function
            print("\n🧪 Testing verify_password function...")
            
            if recruiters:
                test_recruiter = recruiters[0]
                test_email = test_recruiter.email
                test_password = "test123"  # This will fail, but tests the function
                
                # Import database_manager to test
                from database_manager import database_manager
                
                result = database_manager.verify_password(test_email, test_password)
                if result:
                    print(f"   ✅ verify_password working for: {result['email']}")
                    print(f"   📋 Role: {result['role']}")
                else:
                    print(f"   ❌ verify_password failed for: {test_email}")
                    print(f"   🔍 Expected: Function should return None for wrong password")
            
            print("\n🎯 Recruiter Login Status:")
            if len(recruiters) > 0:
                print("   ✅ Database has recruiters")
                print("   ✅ verify_password function exists")
                print("   🔍 Test with actual recruiter credentials")
            else:
                print("   ❌ No recruiters found in database")
                print("   💡 Create test recruiters first")
            
    except Exception as e:
        print(f"   ❌ Error testing recruiter login: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📋 Quick Fix Recommendations:")
    print("1. Test login with actual recruiter credentials")
    print("2. Check verify_password function in database_manager.py")
    print("3. Ensure role-based routing works correctly")
    print("4. Verify session management in login route")
    
    print("\n🌐 Test recruiter login at:")
    print("   http://127.0.0.1:5000/login")
    print("   Use recruiter email and password from database")

if __name__ == "__main__":
    test_recruiter_login()
