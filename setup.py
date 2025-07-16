#!/usr/bin/env python
"""
Setup script for the sectors ticker PDF generator
Run this script to initialize the project
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def setup_project():
    """Set up the Django project"""
    print("🚀 Setting up Sectors Ticker PDF Generator")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("📋 Creating .env file from template...")
            run_command('copy .env.example .env', 'Copy environment template')
            print("⚠️  Please edit .env file with your actual configuration")
        else:
            print("❌ .env.example not found")
    
    # Install dependencies
    print("\n📦 Installing Python dependencies...")
    if not run_command('pip install -r requirements.txt', 'Install dependencies'):
        print("⚠️  You may need to install dependencies manually: pip install -r requirements.txt")
    
    # Run Django migrations
    print("\n🗃️  Setting up database...")
    if not run_command('python manage.py migrate', 'Run database migrations'):
        print("⚠️  Database setup failed. You may need to run migrations manually.")
    
    # Collect static files (if needed)
    print("\n📁 Setting up static files...")
    run_command('python manage.py collectstatic --noinput', 'Collect static files')
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit your .env file with proper credentials")
    print("2. Start the development server: python manage.py runserver")
    print("3. Test the API: python test_generator.py")
    print("\n📚 API Documentation:")
    print("- POST /api/token/ - Get authentication token")
    print("- GET /api/generate-sector-pdf/ - Generate PDF report")
    
    return True

if __name__ == "__main__":
    setup_project()
