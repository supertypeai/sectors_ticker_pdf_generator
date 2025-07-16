#!/usr/bin/env python
"""
Test script for the sectors ticker PDF generator
Run this script to test PDF generation functionality
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sectors_api.settings')
django.setup()

from api.pdf_generator import generate_sector_pdf

def test_pdf_generation():
    """Test PDF generation with sample data"""
    print("Testing PDF generation...")
    
    # Test parameters
    title = "Technology Sector Analysis"
    email = "test@supertype.ai"
    sector = "Technology"
    ticker = "TECH"
    
    try:
        # Generate PDF
        pdf_buffer = generate_sector_pdf(title, email, sector, ticker)
        
        # Save to file
        output_file = "test_sector_report.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ PDF generated successfully: {output_file}")
        print(f"📄 File size: {len(pdf_buffer.getvalue())} bytes")
        
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        return False
    
    return True

def test_api_endpoints():
    """Test API endpoint accessibility"""
    print("\nTesting API configuration...")
    
    try:
        from api.views import SectorTickerPDFAPIView, SupertypeTokenView
        print("✅ API views imported successfully")
        
        from api.urls import urlpatterns
        print("✅ URL patterns configured")
        
        from sectors_api.settings import INSTALLED_APPS
        if 'api' in INSTALLED_APPS:
            print("✅ API app is registered in Django settings")
        else:
            print("❌ API app not found in INSTALLED_APPS")
            
    except Exception as e:
        print(f"❌ Error with API configuration: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Sectors Ticker PDF Generator Test Suite")
    print("=" * 50)
    
    # Test PDF generation
    pdf_success = test_pdf_generation()
    
    # Test API configuration
    api_success = test_api_endpoints()
    
    print("\n" + "=" * 50)
    if pdf_success and api_success:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nNext steps:")
        print("1. Set up your .env file with proper credentials")
        print("2. Run 'python manage.py migrate' to set up the database")
        print("3. Start the server with 'python manage.py runserver'")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        
    print("\n📚 API Usage Example:")
    print("GET /api/generate-sector-pdf/?sector=Technology&ticker=AAPL&title=Tech%20Analysis")
