from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserNotificationChannel

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_alert_settings(sender, instance, created, **kwargs):
    if created:
        UserNotificationChannel.objects.create(user=instance, channel='email', enabled=True)

# Ensure the signal is connected
post_save.connect(create_user_alert_settings, sender=settings.AUTH_USER_MODEL)