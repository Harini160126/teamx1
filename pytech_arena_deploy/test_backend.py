#!/usr/bin/env python3
"""
Simple test for PyTech Arena backend
"""

import os
from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

# Create simple Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Simple test model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))

@app.route('/')
def home():
    return render_template_string("<h1>PyTech Arena - Consolidated Version</h1><p>Backend is working!</p>")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database created successfully")
    
    print("🚀 Starting PyTech Arena (Consolidated Version)...")
    print("📍 URL: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
