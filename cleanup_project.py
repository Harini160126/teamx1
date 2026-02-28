#!/usr/bin/env python3
"""
PyTech Arena - Project Cleanup Script
Removes unnecessary files while keeping essential components
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Remove unnecessary files from the project"""
    
    print("🧹 Starting PyTech Arena Project Cleanup...")
    print("=" * 60)
    
    # Files to keep (essential)
    essential_files = {
        # Core application files
        'app.py',
        'backend.py', 
        'frontend.py',
        'database_manager.py',
        'firebase_config.py',
        
        # Configuration
        '.env',
        '.env.example',
        'requirements.txt',
        '.gitignore',
        
        # Documentation
        'README.md',
        'Presentation.md',
        
        # Assets
        'jntulogo.jpeg',
        
        # Deployment
        'deploy_local.bat',
        'deploy_local.sh',
        'server.py',
        'start.bat',
        'start.sh',
        'netlify.toml',
        
        # Database
        'placement.db',
        
        # Essential directories
        'static/',
        'templates/',
        'uploads/',
        'instance/',
        'migrations/',
        'logs/',
        '__pycache__/',
        'pytech_arena_deploy/'
    }
    
    # Files to remove (non-essential)
    files_to_remove = [
        # Test files
        'test_500_fixed.py',
        'test_admin_dashboard.py',
        'test_admin_dashboard_fix.py',
        'test_admin_features.py',
        'test_all_fixes.py',
        'test_analytics_fix.py',
        'test_complete_login.py',
        'test_enhanced_analytics.py',
        'test_export_and_stats.py',
        'test_firebase_connection.py',
        'test_login_fix.py',
        'test_login_process.py',
        'test_registration_sync.py',
        'test_student_dashboard.py',
        'final_admin_fixes_test.py',
        'final_admin_verification.py',
        'final_comprehensive_test.py',
        'check_firebase_data.py',
        'debug_login.py',
        'firebase_setup_test.py',
        'test_admin_dashboard.py',
        'build.py',
        'create_deployment.py',
        
        # Duplicate/old Firebase files
        'firebase_db.py',
        'firebase_realtime_db.py',
        'init_firebase_db.py',
        'init_professional_db.py',
        
        # Documentation files (keep only essential)
        'ADMIN_DASHBOARD_DISPLAY_FIX.md',
        'ADMIN_DASHBOARD_FIX_REPORT.md',
        'ADMIN_FEATURES_VERIFICATION.md',
        'ADMIN_RECRUITERS_EXPORT_FIXED.md',
        'ALL_ISSUES_FIXED_REPORT.md',
        'BACKEND_DOCUMENTATION.md',
        'DEPLOYMENT_GUIDE.md',
        'DEPLOYMENT_STATUS.md',
        'ENHANCED_ANALYTICS_COMPLETE.md',
        'EXPORT_AND_STATS_FINAL_REPORT.md',
        'FINAL_FIX_REPORT.md',
        'FIREBASE_REALTIME_SETUP.md',
        'FIREBASE_SETUP.md',
        'FIREBASE_SUCCESS_REPORT.md',
        'LOGIN_FIX_REPORT.md',
        'LOGIN_ISSUE_ANALYSIS.md',
        'PROFESSIONAL_DATABASE_REPORT.md',
        'REALTIME_REGISTRATION_GUIDE.md',
        'STUDENT_DASHBOARD_FIX_REPORT.md',
        'dataset_preprocessing_report.md',
        'system_architecture.txt',
        
        # Example files
        'firebase-credentials.example.json',
        
        # Large data files
        'Student_Dataset_200.xlsx',
        'PYTECH Hachkathon.zip'
    ]
    
    # Remove files
    removed_count = 0
    for file_name in files_to_remove:
        file_path = Path(file_name)
        
        if file_path.exists():
            try:
                if file_path.is_file():
                    file_path.unlink()
                    print(f"🗑️  Removed file: {file_name}")
                    removed_count += 1
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    print(f"🗑️  Removed directory: {file_name}")
                    removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {file_name}: {e}")
        else:
            print(f"⚠️  File not found: {file_name}")
    
    # Clean up __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_path = Path(root) / '__pycache__'
            try:
                shutil.rmtree(cache_path)
                print(f"🗑️  Removed cache: {cache_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing cache {cache_path}: {e}")
    
    # Clean up .pyc files
    pyc_count = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = Path(root) / file
                try:
                    pyc_path.unlink()
                    pyc_count += 1
                except Exception as e:
                    print(f"❌ Error removing .pyc file {pyc_path}: {e}")
    
    if pyc_count > 0:
        print(f"🗑️  Removed {pyc_count} .pyc files")
        removed_count += pyc_count
    
    print("\n" + "=" * 60)
    print(f"✅ Cleanup completed!")
    print(f"🗑️  Total files/directories removed: {removed_count}")
    
    # Show remaining essential files
    print("\n📁 Essential files retained:")
    essential_count = 0
    for item in sorted(Path('.').iterdir()):
        if item.name in essential_files or any(item.name.startswith(ef) for ef in essential_files):
            if item.is_file():
                print(f"   📄 {item.name}")
            elif item.is_dir():
                print(f"   📁 {item.name}/")
            essential_count += 1
    
    print(f"\n📊 Essential files retained: {essential_count}")
    
    # Create cleanup report
    report_content = f"""# PyTech Arena - Project Cleanup Report

## 🧹 Cleanup Summary
- **Files Removed**: {removed_count}
- **Essential Files Retained**: {essential_count}
- **Cleanup Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📁 Essential Files Retained
"""
    
    for item in sorted(Path('.').iterdir()):
        if item.name in essential_files or any(item.name.startswith(ef) for ef in essential_files):
            if item.is_file():
                report_content += f"- 📄 `{item.name}`\n"
            elif item.is_dir():
                report_content += f"- 📁 `{item.name}/`\n"
    
    report_content += f"""
## 🚀 Project Status
The project is now clean and ready for deployment with only essential files.

### Core Files:
- `app.py` - Main Flask application
- `backend.py` - Consolidated backend
- `frontend.py` - Consolidated frontend
- `database_manager.py` - Database management
- `firebase_config.py` - Firebase configuration

### Configuration:
- `.env` - Environment variables
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

### Documentation:
- `README.md` - Project documentation
- `Presentation.md` - Project presentation

### Assets:
- `jntulogo.jpeg` - Logo image
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates

### Deployment:
- `deploy_local.bat` - Windows deployment script
- `deploy_local.sh` - Linux deployment script
- `server.py` - Server entry point
- `netlify.toml` - Netlify configuration

### Database:
- `placement.db` - SQLite database
- `migrations/` - Database migrations

## ✅ Ready for Deployment
The project is now optimized and ready for deployment to any platform.
"""
    
    with open('CLEANUP_REPORT.md', 'w') as f:
        f.write(report_content)
    
    print("\n📝 Cleanup report saved to: CLEANUP_REPORT.md")
    print("\n🎉 Project is now clean and optimized!")
    
    return removed_count

if __name__ == "__main__":
    cleanup_project()
