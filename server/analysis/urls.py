"""
URL configuration for analysis app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AnalysisResultViewSet,
    LeakDetectionViewSet,
    ChangeDetectionViewSet,
    EncroachmentDetectionViewSet,
    EmissionDetectionViewSet,
    FacilityMonitoringViewSet,
)

router = DefaultRouter()
router.register(r'results', AnalysisResultViewSet, basename='analysis-result')
router.register(r'leaks', LeakDetectionViewSet, basename='leak-detection')
router.register(r'changes', ChangeDetectionViewSet, basename='change-detection')
router.register(r'encroachments', EncroachmentDetectionViewSet, basename='encroachment-detection')
router.register(r'emissions', EmissionDetectionViewSet, basename='emission-detection')
router.register(r'facilities', FacilityMonitoringViewSet, basename='facility-monitoring')

app_name = 'analysis'

urlpatterns = [
    path('', include(router.urls)),
]

