"""
Serializers for user-related models.
"""

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model

from .models import Organization, UserSettings

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Serializer for user registration.
    """
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'password',
            're_password',
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('re_password'):
            raise serializers.ValidationError({
                're_password': 'Passwords do not match.'
            })
        attrs.pop('re_password', None)
        return super().validate(attrs)


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model.
    """
    class Meta:
        model = Organization
        fields = (
            'name',
            'description',
            'logo',
            'website',
            'phone',
            'address',
            'city',
            'state',
            'country',
            'postal_code',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')


class UserSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for UserSettings model.
    """
    class Meta:
        model = UserSettings
        fields = (
            'theme',
            'notifications_enabled',
            'sound_alerts_enabled',
            'email_notifications',
            'map_default_zoom',
            'map_default_lat',
            'map_default_lng',
            'sidebar_collapsed',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')


class CustomUserSerializer(UserSerializer):
    """
    Serializer for user details.
    """
    organization = OrganizationSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'avatar',
            'is_active',
            'date_joined',
            'updated_at',
            'organization',
            'settings',
        )
        read_only_fields = ('id', 'email', 'date_joined', 'updated_at')


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'avatar',
        )


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    re_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('re_new_password'):
            raise serializers.ValidationError({
                're_new_password': 'New passwords do not match.'
            })
        return attrs

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

