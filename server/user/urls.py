"""
URL configuration for user app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from .views import UserViewSet, OrganizationViewSet, UserSettingsViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'organization', OrganizationViewSet, basename='organization')
router.register(r'settings', UserSettingsViewSet, basename='settings')

app_name = 'user'

urlpatterns = [
    # Djoser endpoints
    path('', include('djoser.urls')),
    
    # JWT endpoints
    path('jwt/create/', TokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),
    path('jwt/blacklist/', TokenBlacklistView.as_view(), name='jwt-blacklist'),
    
    # Custom endpoints
    path('', include(router.urls)),
]

