from rest_framework.views import APIView
from django.http import HttpResponse
from .pdf_generator import generate_sector_pdf  # Adjust import path accordingly
import jwt
import datetime
import sys
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
from dotenv import load_dotenv
load_dotenv()

class HealthCheckView(APIView):
    """Simple health check endpoint"""
    def get(self, request):
        # Check environment variables for debugging
        env_status = {
            'PASSWORD_set': bool(os.environ.get('PASSWORD')),
            'JWT_SECRET_set': bool(os.environ.get('JWT_SECRET')),
            'DEBUG': getattr(settings, 'DEBUG', False)
        }
        
        return Response({
            'status': 'healthy',
            'service': 'Sectors Ticker PDF Generator',
            'version': '1.0.0',
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'environment': env_status
        })

class DebugConfigView(APIView):
    """Debug endpoint to check configuration"""
    def get(self, request):
        return Response({
            'PASSWORD_set': bool(os.environ.get('PASSWORD')),
            'PASSWORD_value': os.environ.get('PASSWORD', 'NOT_SET')[:3] + '***' if os.environ.get('PASSWORD') else 'NOT_SET',
            'JWT_SECRET_set': bool(os.environ.get('JWT_SECRET')),
            'dotenv_loaded': 'dotenv' in sys.modules,
            'settings_debug': getattr(settings, 'DEBUG', False),
            'current_working_directory': os.getcwd()
        })

class SupertypeTokenView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'detail': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

        if not email.endswith('@supertype.ai'):
            return Response({'detail': 'Unauthorized email domain'}, status=status.HTTP_401_UNAUTHORIZED)

        # Debug: Check if PASSWORD environment variable is set
        env_password = os.environ.get('PASSWORD')
        if not env_password:
            return Response({'detail': 'Server configuration error: PASSWORD not set'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if password != env_password:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Debug: Check if JWT_SECRET is set
        jwt_secret = getattr(settings, 'JWT_SECRET', None) or os.environ.get('JWT_SECRET')
        if not jwt_secret:
            return Response({'detail': 'Server configuration error: JWT_SECRET not set'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        payload = {
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS)
        }
        token = jwt.encode(payload, jwt_secret, algorithm=settings.JWT_ALGORITHM)

        return Response({'token': token})


class SectorTickerPDFAPIView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization', '')
        
        # Handle both Bearer token and direct password authentication
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            try:
                # Try to decode JWT token first
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
                # Token is valid, proceed with PDF generation
            except jwt.ExpiredSignatureError:
                return Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.InvalidTokenError:
                # If JWT fails, try direct password comparison
                if token != os.environ.get('PASSWORD', 'default_password'):
                    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # No Bearer token, check for direct password
            token = auth_header
            if token != os.environ.get('PASSWORD', 'default_password'):
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        title_text = request.GET.get('title', 'Sector Ticker Analysis Report')
        email_text = request.GET.get('email', 'human@supertype.ai')
        sector = request.GET.get('sector', '')
        ticker = request.GET.get('ticker', '')
        
        if sector:
            sector = sector.strip()
            sector = ' '.join([w.capitalize() for w in sector.split()])

        try:
            pdf_buffer = generate_sector_pdf(title_text, email_text, sector, ticker)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{title_text}.pdf"'
            return response
        except Exception as e:
            return Response({'detail': f'PDF generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
