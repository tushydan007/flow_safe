"""
Admin configuration for user app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Organization, UserSettings


class OrganizationInline(admin.StackedInline):
    """Inline admin for Organization."""
    model = Organization
    can_delete = False
    verbose_name_plural = 'Organization'
    fk_name = 'user'


class UserSettingsInline(admin.StackedInline):
    """Inline admin for UserSettings."""
    model = UserSettings
    can_delete = False
    verbose_name_plural = 'Settings'
    fk_name = 'user'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom admin for CustomUser model."""
    
    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'avatar')}),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2',
            ),
        }),
    )
    
    inlines = [OrganizationInline, UserSettingsInline]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin for Organization model."""
    
    list_display = (
        'name',
        'user',
        'city',
        'country',
        'created_at',
    )
    list_filter = ('country', 'created_at')
    search_fields = ('name', 'user__email', 'city', 'country')
    ordering = ('name',)
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """Admin for UserSettings model."""
    
    list_display = (
        'user',
        'theme',
        'notifications_enabled',
        'sound_alerts_enabled',
        'created_at',
    )
    list_filter = ('theme', 'notifications_enabled', 'sound_alerts_enabled')
    search_fields = ('user__email',)
    
    readonly_fields = ('created_at', 'updated_at')

