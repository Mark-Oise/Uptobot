from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from apps.monitor.models import Monitor, MonitorLog
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save, sender=MonitorLog)
def create_notification_from_monitor_log(sender, instance, created, **kwargs):
    """Create notifications based on MonitorLog events"""
    if not created:
        return

    monitor = instance.monitor
    
    # Monitor Down Alert - Only notify on first failure after threshold is reached
    if (instance.status in ['failure', 'error'] and 
        monitor.consecutive_failures == monitor.alert_threshold):
        create_notification(
            monitor=monitor,
            notification_type='monitor_down',
            severity='critical',
            message=f"{monitor.name} is down. {instance.error_message or ''}"
        )

    # Monitor Up Alert (Recovery) - Only notify if there was a previous down notification
    elif (instance.status == 'success' and 
          monitor.consecutive_failures == 0 and 
          monitor.availability == 'online' and
          Notification.objects.filter(
              monitor=monitor,
              notification_type='monitor_down',
              created_at__gte=timezone.now() - timedelta(hours=24)
          ).exists()):
        create_notification(
            monitor=monitor,
            notification_type='monitor_up',
            severity='info',
            message=f"{monitor.name} is back online"
        )

@receiver(post_save, sender=Monitor)
def handle_ssl_certificate_notifications(sender, instance, **kwargs):
    """Handle SSL certificate-related notifications"""
    if not instance.url.startswith('https'):
        return

    # Check if we've sent an SSL notification in the last 24 hours
    recent_ssl_notification = Notification.objects.filter(
        monitor=instance,
        notification_type__in=['ssl_invalid', 'ssl_expired', 'ssl_expiring_soon'],
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).exists()

    if recent_ssl_notification:
        return

    ssl_info = instance.get_ssl_certificate_info()
    
    if not ssl_info['valid']:
        create_notification(
            monitor=instance,
            notification_type='ssl_invalid',
            severity='critical',
            message=f"SSL certificate for {instance.name}/{instance.url} is invalid"
        )
        return

    if ssl_info['expiry_date']:
        days_until_expiry = (ssl_info['expiry_date'] - timezone.now()).days
        
        # SSL Expired
        if days_until_expiry <= 0:
            create_notification(
                monitor=instance,
                notification_type='ssl_expired',
                severity='critical',
                message=f"SSL certificate for {instance.name}/{instance.url} has expired"
            )
        
        # SSL Expiring Soon (notify at 30, 14, and 7 days)
        elif days_until_expiry in [30, 14, 7]:
            create_notification(
                monitor=instance,
                notification_type='ssl_expiring_soon',
                severity='warning',
                message=f"SSL certificate for {instance.name}/{instance.url} expires in {days_until_expiry} days"
            )

def create_notification(monitor, notification_type, severity, message):
    """Helper function to create notifications and send via WebSocket"""
    # Create the notification
    notification = Notification.objects.create(
        user=monitor.user,
        title=f"{notification_type.replace('_', ' ').title()}: {monitor.name}",
        message=message,
        notification_type=notification_type,
        severity=severity,
        monitor=monitor
    )
    
    return notification
    