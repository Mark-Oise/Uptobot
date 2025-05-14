from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from apps.monitor.models import Monitor, MonitorLog
from .models import Alert, AlertDelivery
from .tasks import send_notification
from apps.accounts.models import UserAlertSettings
from apps.alerts.models import BatchedAlert


@receiver(post_save, sender=MonitorLog)
def handle_monitor_log_alerts(sender, instance, created, **kwargs):
    if not created:
        return

    monitor = instance.monitor
    last_24h = timezone.now() - timedelta(hours=24)
    
    # Monitor Down Alert - Only on first failure after threshold
    if (instance.status in ['failure', 'error'] and 
        monitor.consecutive_failures == monitor.alert_threshold):
        create_alert(
            monitor=monitor,
            alert_type='monitor_down',
            severity='critical',
            message=f"{monitor.name} is down. {instance.error_message or ''}"
        )

    # Monitor Up Alert - Only if there was a previous down alert
    elif (instance.status == 'success' and 
          monitor.consecutive_failures == 0 and 
          monitor.availability == 'online'):
        # Check for recent down alert in the last 24 hours
        recent_down_alert = Alert.objects.filter(
            monitor=monitor,
            alert_type='monitor_down',
            created_at__gte=last_24h
        ).exists()
        
        if recent_down_alert:
            create_alert(
                monitor=monitor,
                alert_type='monitor_up',
                severity='info',
                message=f"{monitor.name} is back online"
            )

@receiver(post_save, sender=Monitor)
def handle_ssl_certificate_alerts(sender, instance, **kwargs):
    """Handle SSL certificate-related alerts with deduplication"""
    
    if not instance.url.startswith('https'):
        return

    ssl_info = instance.get_ssl_certificate_info()
    
    if ssl_info['expiry_date']:
        days_until_expiry = (ssl_info['expiry_date'] - timezone.now()).days
        
        # SSL Expired - only alert once
        if days_until_expiry <= 0:
            create_alert(
                monitor=instance,
                alert_type='ssl_expired',
                severity='critical',
                message=f"SSL certificate for {instance.name} has expired"
            )
        
        # SSL Expiring Soon (notify at 30, 14, and 7 days)
        elif days_until_expiry in [30, 14, 7]:
            create_alert(
                monitor=instance,
                alert_type='ssl_expiring_soon',
                severity='warning',
                message=f"SSL certificate for {instance.name} expires in {days_until_expiry} days"
            )


def create_alert(monitor, alert_type, severity, message):
    """Helper function to create alerts with deduplication logic"""
    
    # Don't create duplicate alerts of the same type for the same monitor in a short period
    recent_similar_alert = Alert.objects.filter(
        monitor=monitor,
        alert_type=alert_type,
        created_at__gte=timezone.now() - timedelta(hours=1)
    ).exists()
    
    if recent_similar_alert:
        # Skip creating duplicate alert
        return None
    
    # Create the new alert
    return Alert.objects.create(
        monitor=monitor,
        alert_type=alert_type,
        severity=severity,
        message=message
    )



@receiver(post_save, sender=Alert)
def handle_alert_delivery(sender, instance, created, **kwargs):
    """Handle the delivery of alerts through all enabled notification channels"""
    if not created:
        return
    
    user = instance.monitor.user
    
    # Get all enabled notification channels for the user
    enabled_channels = user.notification_channels.filter(enabled=True)
    
    for channel in enabled_channels:
        # Create delivery for each enabled channel
        delivery = AlertDelivery.objects.create(
            alert=instance,
            notification_channel=channel,
            recipient=user.email if channel.channel == 'email' else None,
            status='pending'
        )
        
        # Send notification through appropriate channel
        send_notification.delay(delivery.id)