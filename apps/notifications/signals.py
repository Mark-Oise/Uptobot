from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from apps.monitor.models import Monitor, MonitorLog
from .models import Notification


@receiver(post_save, sender=MonitorLog)
def create_notification_from_monitor_log(sender, instance, created, **kwargs):
    """Create notifications based on MonitorLog events"""
    if not created:
        return

    monitor = instance.monitor
    
    # Monitor Down Alert
    if (instance.status in ['failure', 'error'] and 
        monitor.consecutive_failures >= monitor.alert_threshold):
        create_notification(
            monitor=monitor,
            notification_type='monitor_down',
            severity='critical',
            message=f"{monitor.name} is down. {instance.error_message or ''}"
        )

    # Monitor Up Alert (Recovery)
    elif (instance.status == 'success' and 
          monitor.consecutive_failures == 0 and 
          monitor.availability == 'online'):
        create_notification(
            monitor=monitor,
            notification_type='monitor_up',
            severity='info',
            message=f"{monitor.name} is back online"
        )

    # Availability Alert
    if monitor.get_uptime_percentage(days=1) < 90:
        create_notification(
            monitor=monitor,
            notification_type='availability',
            severity='warning',
            message=f"{monitor.name} availability has dropped below 90%"
        )

    # Response Time and Latency Alerts
    if instance.status == 'success' and instance.response_time:
        # Response time threshold
        if instance.response_time > 2000:
            create_notification(
                monitor=monitor,
                notification_type='response_time',
                severity='warning',
                message=f"{monitor.name} response time is high: {instance.response_time}ms"
            )
        
        # Latency spike
        avg_response_time = monitor.get_average_response_time(days=1)
        if avg_response_time and instance.response_time > (avg_response_time * 3):
            create_notification(
                monitor=monitor,
                notification_type='latency_spike',
                severity='warning',
                message=f"{monitor.name} is experiencing unusually high latency"
            )

@receiver(post_save, sender=Monitor)
def handle_ssl_certificate_notifications(sender, instance, **kwargs):
    """Handle SSL certificate-related notifications"""
    
    if not instance.url.startswith('https'):
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
        
        # SSL Expiring Soon (30 days or less)
        elif days_until_expiry <= 30:
            create_notification(
                monitor=instance,
                notification_type='ssl_expiring_soon',
                severity='warning',
                message=f"SSL certificate for {instance.name}/{instance.url} expires in {days_until_expiry} days"
            )

def create_notification(monitor, notification_type, severity, message):
    """Helper function to create notifications"""
    Notification.objects.create(
        user=monitor.user,
        title=f"{notification_type.replace('_', ' ').title()}: {monitor.name}",
        message=message,
        notification_type=notification_type,
        severity=severity,
        monitor=monitor
    )