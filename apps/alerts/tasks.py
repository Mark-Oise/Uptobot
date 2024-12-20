from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from .models import AlertDelivery

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)

def send_alert_email(self, delivery_id):
    """
    Task to send alert emails with retry mechanism
    """
    try:
        delivery = AlertDelivery.objects.select_related(
            'alert', 
            'alert__monitor'
        ).get(id=delivery_id)
        
        if delivery.status == 'sent':
            return "Alert already sent"

        alert = delivery.alert
        monitor = alert.monitor

        # Prepare email content
        subject = f"[{alert.get_severity_display()}] {alert.get_alert_type_display()}: {monitor.name}"
        
        # Simple email message
        message = f"""
Monitor Alert: {monitor.name}
URL: {monitor.url}
Status: {alert.get_alert_type_display()}
Severity: {alert.get_severity_display()}
Time: {alert.created_at}

Message:
{alert.message}

View Monitor: {settings.BASE_URL}{monitor.get_absolute_url()}
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
