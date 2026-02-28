#!/bin/bash

# PyTech Arena Local Deployment Script
# This script sets up and runs the PyTech Arena application locally

echo "🚀 Starting PyTech Arena Local Deployment..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
EOF
    echo "✅ .env template created. Please update with your actual configuration."
fi

# Set environment variables
export FLASK_ENV=development
export FLASK_DEBUG=True

# Start the application
echo "🌐 Starting PyTech Arena application..."
echo "📍 Application will be available at: http://localhost:5000"
echo "🔑 Admin Login: placement@jntugv.edu.in / Admin@2026"
echo "👨‍🎓 Student Login: arun.kumar@jntugv.edu.in / Student@2026"
echo "=================================="
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask application
python app.py
