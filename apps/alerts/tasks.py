from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from .models import AlertDelivery, BatchedAlert
from datetime import timedelta
from django.db.models import Count
from collections import defaultdict
import requests

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def send_notification(self, delivery_id):
    """Task to send notifications through enabled channels"""
    try:
        delivery = AlertDelivery.objects.select_related(
            'alert', 
            'alert__monitor',
            'notification_channel'
        ).get(id=delivery_id)
        
        if delivery.status == 'sent':
            return "Alert already sent"

        alert = delivery.alert
        monitor = alert.monitor
        channel = delivery.notification_channel

        # Prepare basic message content
        message = f"[{alert.get_severity_display()}] {monitor.name}: {alert.message}"
        monitor_url = f"{settings.BASE_URL}/monitors/{monitor.slug}/"

        # Send based on channel type
        if channel.channel == 'email':
            send_email_alert(delivery, message, monitor_url)
        elif channel.channel == 'slack':
            send_slack_alert(delivery, message, monitor_url)
        elif channel.channel == 'discord':
            send_discord_alert(delivery, message, monitor_url)

        # Update delivery status
        delivery.status = 'sent'
        delivery.sent_at = timezone.now()
        delivery.save()

        return f"Alert sent successfully via {channel.channel}"

    except Exception as e:
        delivery.retry_count += 1
        delivery.error_message = str(e)
        delivery.save()
        
        if delivery.retry_count <= 3:
            raise self.retry(exc=e)
        else:
            delivery.status = 'failed'
            delivery.save()
            return f"Failed to send alert after {delivery.retry_count} retries: {str(e)}"

def send_email_alert(delivery, message, monitor_url):
    """Helper function to send email alerts"""
    subject = f"Monitor Alert: {delivery.alert.monitor.name}"
    send_mail(
        subject=subject,
        message=f"{message}\n\nView Details: {monitor_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[delivery.recipient],
        fail_silently=False,
    )

def send_slack_alert(delivery, message, monitor_url):
    """Helper function to send Slack alerts"""
    webhook_url = delivery.notification_channel.webhook_url
    if not webhook_url:
        raise ValueError("Slack webhook URL not configured")

    payload = {
        "text": f"{message}\nView Details: {monitor_url}",
    }
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()


def send_discord_alert(delivery, message, monitor_url):
    """Helper function to send Discord alerts"""
    webhook_url = delivery.notification_channel.webhook_url
    if not webhook_url:
        raise ValueError("Discord webhook URL not configured")

    payload = {
        "content": f"{message}\nView Details: {monitor_url}",
    }
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()


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
