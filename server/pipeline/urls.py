"""
URL configuration for pipeline app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PipelineRouteViewSet, SatelliteImageViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'routes', PipelineRouteViewSet, basename='pipeline-route')
router.register(r'images', SatelliteImageViewSet, basename='satellite-image')
router.register(r'alerts', AlertViewSet, basename='alert')

app_name = 'pipeline'

urlpatterns = [
    path('', include(router.urls)),
]

