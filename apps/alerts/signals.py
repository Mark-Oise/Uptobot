from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from apps.monitor.models import Monitor, MonitorLog
from .models import Alert, AlertDelivery
from .tasks import send_alert_email


@receiver(post_save, sender=MonitorLog)
def handle_monitor_log_alerts(sender, instance, created, **kwargs):
    if not created:
        return

    monitor = instance.monitor
    
    # Monitor Down Alert
    if (instance.status in ['failure', 'error'] and 
        monitor.consecutive_failures >= monitor.alert_threshold):
        create_alert(
            monitor=monitor,
            alert_type='monitor_down',
            severity='critical',
            message=f"{monitor.name} is down. {instance.error_message or ''}"
        )

    # Monitor Up Alert (Recovery)
    elif (instance.status == 'success' and 
          monitor.consecutive_failures == 0 and 
          monitor.availability == 'online'):
        create_alert(
            monitor=monitor,
            alert_type='monitor_up',
            severity='info',
            message=f"{monitor.name} is back online"
        )

    # Availability Alert
    if monitor.get_uptime_percentage(days=1) < 90:  # Simple 90% threshold
        create_alert(
            monitor=monitor,
            alert_type='availability',
            severity='warning',
            message=f"{monitor.name} availability has dropped below 90%"
        )

    # Response Time and Latency Alerts
    if instance.status == 'success' and instance.response_time:
        # Simple response time threshold (2 seconds)
        if instance.response_time > 2000:
            create_alert(
                monitor=monitor,
                alert_type='response_time',
                severity='warning',
                message=f"{monitor.name} response time is high: {instance.response_time}ms"
            )
        
        # Simple latency spike detection (3x the average)
        avg_response_time = monitor.get_average_response_time(days=1)
        if avg_response_time and instance.response_time > (avg_response_time * 3):
            create_alert(
                monitor=monitor,
                alert_type='latency_spike',
                severity='warning',
                message=f"{monitor.name} is experiencing unusually high latency"
            )

@receiver(post_save, sender=Monitor)
def handle_ssl_certificate_alerts(sender, instance, **kwargs):
    """Handle SSL certificate-related alerts"""
    
    if not instance.url.startswith('https'):
        return

    ssl_info = instance.get_ssl_certificate_info()
    
    if not ssl_info['valid']:
        create_alert(
            monitor=instance,
            alert_type='ssl_invalid',
            severity='critical',
            message=f"SSL certificate for {instance.name} is invalid"
        )
        return

    if ssl_info['expiry_date']:
        days_until_expiry = (ssl_info['expiry_date'] - timezone.now()).days
        
        # SSL Expired
        if days_until_expiry <= 0:
            create_alert(
                monitor=instance,
                alert_type='ssl_expired',
                severity='critical',
                message=f"SSL certificate for {instance.name} has expired"
            )
        
        # SSL Expiring Soon (30 days or less)
        elif days_until_expiry <= 30:
            create_alert(
                monitor=instance,
                alert_type='ssl_expiring_soon',
                severity='warning',
                message=f"SSL certificate for {instance.name} expires in {days_until_expiry} days"
            )

def create_alert(monitor, alert_type, severity, message):
    """Helper function to create alerts and prevent duplicates"""
    
    # Prevent duplicate alerts within a time window
    recent_similar_alert = Alert.objects.filter(
        monitor=monitor,
        alert_type=alert_type,
        created_at__gte=timezone.now() - timedelta(hours=1)  # 1-hour window
    ).exists()

    if not recent_similar_alert:
        Alert.objects.create(
            monitor=monitor,
            alert_type=alert_type,
            severity=severity,
            message=message
        )

@receiver(post_save, sender=Alert)
def handle_alert_delivery(sender, instance, created, **kwargs):
    """Handle the delivery of alerts via email"""
    if not created:
        return

    delivery = AlertDelivery.objects.create(
        alert=instance,
        recipient=instance.monitor.user.email,
        status='pending'
    )

    send_alert_email.delay(delivery.id)
