from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserAlertSettings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_alert_settings(sender, instance, created, **kwargs):
    if created:
        UserAlertSettings.objects.create(user=instance)

# Ensure the signal is connected
post_save.connect(create_user_alert_settings, sender=settings.AUTH_USER_MODEL)