"""
Signals for user app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Organization, UserSettings

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create Organization and UserSettings when a new user is created.
    """
    if created:
        # Create default organization for user
        Organization.objects.get_or_create(
            user=instance,
            defaults={
                'name': f"{instance.get_full_name()}'s Organization"
            }
        )
        
        # Create default settings for user
        UserSettings.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save Organization and UserSettings when user is saved.
    """
    try:
        instance.organization.save()
    except Organization.DoesNotExist:
        pass
    
    try:
        instance.settings.save()
    except UserSettings.DoesNotExist:
        pass

