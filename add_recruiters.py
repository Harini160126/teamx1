#!/usr/bin/env python3
"""
Quick fix for recruiter login - add test recruiters
"""

import sqlite3
import hashlib
from werkzeug.security import generate_password_hash

def add_test_recruiters():
    """Add test recruiters directly to SQLite database"""
    
    print("🔧 Adding Test Recruiters to Database")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect('placement.db')
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ Users table not found. Run python app.py first to create tables.")
            return False
        
        # Clear existing recruiters (optional)
        cursor.execute("DELETE FROM user WHERE role = 'recruiter'")
        conn.commit()
        print("🗑️ Cleared existing recruiters")
        
        # Add test recruiters
        recruiters = [
            ('TechCorp Recruiter', 'techcorp@pytecharena.com', 'Recruiter@2026', 'Tech Corporation'),
            ('StartupXYZ Recruiter', 'startupxyz@pytecharena.com', 'Recruiter@2026', 'StartupXYZ Technologies'),
            ('Innovation Labs Recruiter', 'innovation@pytecharena.com', 'Recruiter@2026', 'Innovation Labs')
        ]
        
        for name, email, password, company in recruiters:
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO user (name, email, password_hash, role, company_name, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (name, email, password_hash, 'recruiter', company))
            print(f"   ✅ Added: {name} ({email})")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Successfully added {len(recruiters)} test recruiters!")
        print("\n📋 Test Login Credentials:")
        for i, (name, email, password, company) in enumerate(recruiters, 1):
            print(f"   {i}. {email} / {password}")
        
        print("\n🌐 Next Steps:")
        print("1. Start application: python app.py")
        print("2. Go to: http://127.0.0.1:5000/login")
        print("3. Use any test recruiter credentials above")
        print("4. Should redirect to recruiter dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 PyTech Arena - Recruiter Login Fix")
    print("=" * 50)
    
    success = add_test_recruiters()
    
    if success:
        print("\n🎉 Recruiter accounts added successfully!")
        print("📖 The recruiter login issue should now be FIXED!")
    else:
        print("\n❌ Failed to add recruiters")
        print("📋 Check if placement.db exists and is writable")
