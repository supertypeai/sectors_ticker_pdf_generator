from django.urls import path
from .views import SectorTickerPDFAPIView, SupertypeTokenView, HealthCheckView, DebugConfigView

urlpatterns = [
    path('', HealthCheckView.as_view(), name='health-check'),
    path('health/', HealthCheckView.as_view(), name='health-check-alt'),
    path('debug/', DebugConfigView.as_view(), name='debug-config'),
    path('generate-sector-pdf/', SectorTickerPDFAPIView.as_view(), name='generate-sector-pdf'),
    path('token/', SupertypeTokenView.as_view(), name='api_token_auth'),
]
