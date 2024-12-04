from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from apps.alerts.models import Alert
from .models import Notification

@receiver(post_save, sender=Alert)
def handle_alert(sender, instance, created, **kwargs):
    if created:
        # Create in-app notification
        notification = Notification.objects.create(
            user=instance.monitor.user,
            title=f"Alert: {instance.monitor.name}",
            message=instance.message,
            notification_type='monitor_down' if instance.alert_type == 'availability' else 'alert_threshold',
            severity='critical' if instance.alert_type == 'availability' else 'warning',
            monitor=instance.monitor
        )

        # Get user alert settings
        alert_settings = instance.monitor.user.useralertsettings

        # Send email if enabled
        if alert_settings.email_alerts_enabled:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.monitor.user.email],
                fail_silently=True,
            )