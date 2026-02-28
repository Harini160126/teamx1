@echo off
REM PyTech Arena Local Deployment Script for Windows
REM This script sets up and runs the PyTech Arena application locally

echo 🚀 Starting PyTech Arena Local Deployment...
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not installed. Please install pip.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating template...
    (
        echo # Firebase Configuration
        echo FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-credentials.json
        echo FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
        echo.
        echo # Flask Configuration
        echo FLASK_ENV=development
        echo FLASK_DEBUG=True
        echo SECRET_KEY=your-secret-key-here
        echo.
        echo # Email Configuration ^(Optional^)
        echo MAIL_SERVER=smtp.gmail.com
        echo MAIL_PORT=587
        echo MAIL_USE_TLS=True
        echo MAIL_USERNAME=your-email@gmail.com
        echo MAIL_PASSWORD=your-app-password
    ) > .env
    echo ✅ .env template created. Please update with your actual configuration.
)

REM Set environment variables
set FLASK_ENV=development
set FLASK_DEBUG=True

REM Start the application
echo 🌐 Starting PyTech Arena application...
echo 📍 Application will be available at: http://localhost:5000
echo 🔑 Admin Login: placement@jntugv.edu.in / Admin@2026
echo 👨‍🎓 Student Login: arun.kumar@jntugv.edu.in / Student@2026
echo ==================================
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask application
python app.py

pause
