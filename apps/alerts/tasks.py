from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from .models import AlertDelivery, BatchedAlert
from datetime import timedelta
from django.db.models import Count
from collections import defaultdict

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def send_alert_email(self, delivery_id):
    """Task to send alert emails with retry mechanism"""
    try:
        delivery = AlertDelivery.objects.select_related(
            'alert', 
            'alert__monitor'
        ).get(id=delivery_id)
        
        if delivery.status == 'sent':
            return "Alert already sent"

        alert = delivery.alert
        monitor = alert.monitor

        # Prepare email content with improved readability
        subject = f"[{alert.get_severity_display()}] {alert.get_alert_type_display()}: {monitor.name}"
        
        # Use direct URL construction instead of reverse to avoid NoReverseMatch errors
        monitor_url = f"{settings.BASE_URL}/monitors/{monitor.slug}/"
        
        # Simplified but clear email message
        message = f"""
MONITOR ALERT: {monitor.name}
--------------------------------------------------
URL: {monitor.url}
Status: {alert.get_alert_type_display()}
Severity: {alert.get_severity_display()}
Time: {alert.created_at.strftime('%Y-%m-%d %H:%M')}

Message:
{alert.message}

View Monitor Details: {monitor_url}
        """

        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[delivery.recipient],
            fail_silently=False,
        )

        # Update delivery status
        delivery.status = 'sent'
        delivery.sent_at = timezone.now()
        delivery.save()

        return f"Alert email sent successfully to {delivery.recipient}"

    except AlertDelivery.DoesNotExist:
        return f"Alert delivery {delivery_id} not found"
    
    except Exception as e:
        # Update retry count and error message
        delivery.retry_count += 1
        delivery.error_message = str(e)
        delivery.save()
        
        # Retry with exponential backoff if under max retries
        if delivery.retry_count <= 3:
            raise self.retry(exc=e, countdown=300 * (2 ** (delivery.retry_count - 1)))
        else:
            delivery.status = 'failed'
            delivery.save()
            return f"Failed to send alert after {delivery.retry_count} retries: {str(e)}"


@shared_task
def process_batched_alerts():
    """Periodic task to process and send batched alerts with basic grouping"""
    now = timezone.now()
    
    # Get all unsent batched alerts
    batched_alerts = BatchedAlert.objects.filter(
        sent=False
    ).select_related('user').prefetch_related('alerts', 'user__useralertsettings')

    for batch in batched_alerts:
        settings = batch.user.useralertsettings
        
        # Check if it's time to send based on frequency
        if settings.alert_frequency == 'daily':
            if (now - settings.last_alert_sent) < timedelta(days=1):
                continue
        elif settings.alert_frequency == 'weekly':
            if (now - settings.last_alert_sent) < timedelta(weeks=1):
                continue
                
        # Group alerts by monitor for cleaner presentation
        alerts_by_monitor = defaultdict(list)
        for alert in batch.alerts.select_related('monitor').order_by('created_at'):
            alerts_by_monitor[alert.monitor].append(alert)
            
        # Prepare digest email content
        subject = f"Monitor Alert Digest for {batch.user.username}"
        message = "Monitor Alert Summary\n\n"
        
        for monitor, alerts in alerts_by_monitor.items():
            message += f"\n{monitor.name} ({monitor.url}):\n"
            message += "-" * 50 + "\n"
            for alert in alerts:
                message += f"- [{alert.get_severity_display()}] {alert.created_at.strftime('%Y-%m-%d %H:%M')}: {alert.message}\n"
            
            # Use slug instead of ID in URL construction
            monitor_url = f"{settings.BASE_URL}/monitors/{monitor.slug}/"
            message += f"\nView Monitor: {monitor_url}\n"
        
        # Send digest email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[batch.user.email],
            fail_silently=False,
        )
        
        # Update batch and settings
        batch.sent = True
        batch.save()
        settings.last_alert_sent = now
        settings.save()
