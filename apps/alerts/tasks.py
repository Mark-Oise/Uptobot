from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import AlertDelivery
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


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

        # Simple message format for all channels
        message = f"[{alert.get_severity_display()}] {monitor.name}: {alert.message}\n\nView Details: {settings.BASE_URL}/monitors/{monitor.slug}/"

        # Send based on channel type
        if channel.channel == 'email':
            send_email_alert(delivery, message)
        elif channel.channel == 'slack':
            send_slack_alert(delivery, message)
        elif channel.channel == 'discord':
            send_discord_alert(delivery, message)

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



def send_email_alert(delivery, message):
    """Send simple email alert"""
    subject = f"Monitor Alert: {delivery.alert.monitor.name}"
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[delivery.notification_channel.user.email],
        fail_silently=False,
    )



def send_slack_alert(delivery, message):
    """Send simple Slack alert"""
    if not delivery.notification_channel.oauth_token:
        raise Exception("Slack not properly connected")

    client = WebClient(token=delivery.notification_channel.oauth_token)
    client.chat_postMessage(
        channel=delivery.notification_channel.channel_id,
        text=message,
        unfurl_links=False,
        unfurl_media=False,
        parse='mrkdwn'
    )


def send_discord_alert(delivery, message):
    """Send Discord alert with webhook"""
    if not delivery.notification_channel.oauth_token:
        raise Exception("Discord not properly connected")

    # For Discord, we'll use the bot token to send messages directly to a channel
    headers = {
        'Authorization': f'Bot {delivery.notification_channel.oauth_token}',
        'Content-Type': 'application/json'
    }
    
    # Create a rich embed for better formatting
    payload = {
        'content': '',
        'embeds': [{
            'title': 'Alert Notification',
            'description': message,
            'color': 16711680 if 'critical' in message.lower() else 5814783,  # Red for critical, blue for others
            'footer': {
                'text': 'Sent by Uptobot'
            },
            'timestamp': timezone.now().isoformat()
        }]
    }

    response = requests.post(
        f'https://discord.com/api/v10/channels/{delivery.notification_channel.channel_id}/messages',
        headers=headers,
        json=payload
    )
    response.raise_for_status()


