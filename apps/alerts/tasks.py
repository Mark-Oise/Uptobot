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
        
        # Create context for HTML template
        context = {
            'monitor_name': monitor.name,
            'monitor_url': monitor.url,
            'alert_type': alert.get_alert_type_display(),
            'alert_severity': alert.get_severity_display(),
            'alert_time': alert.created_at.strftime('%B %d, %Y at %H:%M UTC'),
            'alert_message': alert.message,
            'monitor_details_url': monitor_url,
            'response_code': getattr(alert, 'response_code', 'N/A'),
            'response_time': getattr(alert, 'response_time', 'N/A'),
        }
        
        # Render HTML email
        html_message = render_to_string('alerts/incident_email.html', context)
        
        # Plain text fallback
        plain_message = f"""
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

        # Send email with HTML content
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[delivery.recipient],
            fail_silently=False,
            html_message=html_message,
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
    """Periodic task to process and send batched alerts with HTML template"""
    now = timezone.now()
    
    # Get all unsent batched alerts
    batched_alerts = BatchedAlert.objects.filter(
        sent=False
    ).select_related('user').prefetch_related('alerts', 'alerts__monitor')

    for batch in batched_alerts:
        settings = batch.user.useralertsettings
        
        # Check if it's time to send based on frequency
        if settings.alert_frequency == 'daily':
            if (now - settings.last_alert_sent) < timedelta(days=1):
                continue
        elif settings.alert_frequency == 'weekly':
            if (now - settings.last_alert_sent) < timedelta(weeks=1):
                continue
                
        # Group alerts by monitor and prepare monitor stats
        monitors_data = {}
        for alert in batch.alerts.select_related('monitor').order_by('created_at'):
            monitor = alert.monitor
            if monitor not in monitors_data:
                monitors_data[monitor] = {
                    'name': monitor.name,
                    'url': monitor.url,
                    'status': monitor.availability,
                    'uptime': monitor.get_uptime_percentage(days=7),
                    'avg_response': monitor.get_average_response_time(days=7),
                    'incidents': [],
                    'health_score': monitor.get_health_score(),
                    'slug': monitor.slug
                }
            monitors_data[monitor]['incidents'].append({
                'severity': alert.get_severity_display(),
                'timestamp': alert.created_at,
                'message': alert.message
            })

        # Prepare context for HTML template
        context = {
            'user': batch.user,
            'monitors': monitors_data.values(),
            'report_period': f"{(now - timedelta(days=7)).strftime('%B %d')}-{now.strftime('%d, %Y')}",
            'base_url': settings.BASE_URL
        }
        
        # Render HTML email
        html_message = render_to_string('alerts/batched_alerts.html', context)
        
        # Create plain text version as fallback
        plain_message = "Monitor Alert Summary\n\n"
        for monitor_data in monitors_data.values():
            plain_message += f"\n{monitor_data['name']} ({monitor_data['url']})\n"
            plain_message += f"Status: {monitor_data['status']}\n"
            plain_message += f"Uptime: {monitor_data['uptime']}%\n"
            plain_message += f"Average Response: {monitor_data['avg_response']}ms\n"
            plain_message += "Incidents:\n"
            for incident in monitor_data['incidents']:
                plain_message += f"- [{incident['severity']}] {incident['timestamp'].strftime('%Y-%m-%d %H:%M')}: {incident['message']}\n"
            plain_message += f"\nView Monitor: {settings.BASE_URL}/monitors/{monitor_data['slug']}/\n"

        # Send digest email
        send_mail(
            subject=f"Your {'daily' if settings.alert_frequency == 'daily' else 'weekly'} alert digest is ready!",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[batch.user.email],
            fail_silently=False,
            html_message=html_message
        )
        
        # Update batch and settings
        batch.sent = True
        batch.save()
        settings.last_alert_sent = now
        settings.save()
