#!/usr/bin/env python
"""
Quick debug script to test authentication
"""

import requests
import json
import os
from pathlib import Path

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000/api"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_debug_config():
    """Test the debug configuration endpoint"""
    print("\n🔍 Testing debug configuration...")
    try:
        response = requests.get(f"{BASE_URL}/debug/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Debug config failed: {e}")
        return False

def test_token_generation():
    """Test token generation"""
    print("\n🔍 Testing token generation...")
    
    # Read credentials from .env file
    env_file = Path(".env")
    password = None
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('PASSWORD'):
                    password = line.split('=')[1].strip().strip('"').strip("'")
                    break
    
    if not password:
        print("❌ Could not find PASSWORD in .env file")
        return False
    
    print(f"Using password: {password[:3]}***")
    
    data = {
        "email": "test@supertype.ai",
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/token/", json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"✅ Token generated: {token[:20]}...")
            return token
        else:
            print("❌ Token generation failed")
            return None
            
    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return None

def test_pdf_generation(token=None):
    """Test PDF generation"""
    print("\n🔍 Testing PDF generation...")
    
    if not token:
        # Try with direct password authentication
        env_file = Path(".env")
        password = None
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('PASSWORD'):
                        password = line.split('=')[1].strip().strip('"').strip("'")
                        break
        
        if password:
            headers = {"Authorization": password}
            print(f"Using direct password auth: {password[:3]}***")
        else:
            print("❌ No token or password available")
            return False
    else:
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Using Bearer token: {token[:20]}...")
    
    params = {
        "sector": "Technology",
        "ticker": "AAPL",
        "title": "Test Report"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/generate-sector-pdf/", 
                              headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ PDF generated successfully! Size: {len(response.content)} bytes")
            # Save the PDF for verification
            with open("test_output.pdf", "wb") as f:
                f.write(response.content)
            print("📄 PDF saved as test_output.pdf")
            return True
        else:
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return False

def main():
    print("🚀 Sectors Ticker PDF Generator - Authentication Debug")
    print("=" * 60)
    
    # Test 1: Health check
    health_ok = test_health_check()
    
    # Test 2: Debug config
    debug_ok = test_debug_config()
    
    # Test 3: Token generation
    token = test_token_generation()
    
    # Test 4: PDF generation
    pdf_ok = test_pdf_generation(token)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Debug Config: {'✅' if debug_ok else '❌'}")
    print(f"Token Generation: {'✅' if token else '❌'}")
    print(f"PDF Generation: {'✅' if pdf_ok else '❌'}")
    
    if not health_ok:
        print("\n💡 Make sure the Django server is running:")
        print("   python manage.py runserver")
    
    if health_ok and not token:
        print("\n💡 Check your .env file and make sure PASSWORD is set correctly")
    
    if token and not pdf_ok:
        print("\n💡 Check server logs for PDF generation errors")

if __name__ == "__main__":
    main()
