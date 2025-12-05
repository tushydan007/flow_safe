"""
Views for user-related operations.
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Organization, UserSettings
from .serializers import (
    CustomUserSerializer,
    UserUpdateSerializer,
    OrganizationSerializer,
    UserSettingsSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user operations.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Return the current user only."""
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        """Return the current user."""
        return self.request.user

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """
        Get or update the current user's profile.
        """
        user = request.user

        if request.method == 'GET':
            serializer = CustomUserSerializer(user)
            return Response({
                'success': True,
                'data': serializer.data
            })

        elif request.method == 'PATCH':
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Profile updated successfully.',
                    'data': CustomUserSerializer(user).data
                })
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """
        Change user password.
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'success': True,
                'message': 'Password changed successfully.'
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='delete-account')
    def delete_account(self, request):
        """
        Delete user account.
        """
        user = request.user
        user.is_active = False
        user.save()
        return Response({
            'success': True,
            'message': 'Account deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for organization operations.
    """
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Return the organization for the current user."""
        return Organization.objects.filter(user=self.request.user)

    def get_object(self):
        """Return the current user's organization."""
        return get_object_or_404(Organization, user=self.request.user)

    def list(self, request, *args, **kwargs):
        """Get the current user's organization."""
        try:
            organization = Organization.objects.get(user=request.user)
            serializer = self.get_serializer(organization)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Organization.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Organization not found.'
            }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """Create organization for current user."""
        if Organization.objects.filter(user=request.user).exists():
            return Response({
                'success': False,
                'message': 'Organization already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                'success': True,
                'message': 'Organization created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update the current user's organization."""
        organization = self.get_object()
        serializer = self.get_serializer(
            organization,
            data=request.data,
            partial=kwargs.get('partial', False)
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Organization updated successfully.',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user settings operations.
    """
    serializer_class = UserSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return settings for the current user."""
        return UserSettings.objects.filter(user=self.request.user)

    def get_object(self):
        """Return the current user's settings."""
        settings, _ = UserSettings.objects.get_or_create(user=self.request.user)
        return settings

    def list(self, request, *args, **kwargs):
        """Get the current user's settings."""
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        """Update the current user's settings."""
        settings = self.get_object()
        serializer = self.get_serializer(
            settings,
            data=request.data,
            partial=kwargs.get('partial', False)
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Settings updated successfully.',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

