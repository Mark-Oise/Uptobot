from django.db import models
from django.conf import settings
from apps.monitor.models import Monitor

class Alert(models.Model):
    ALERT_TYPES = [
        ('availability', 'Availability'),
        ('response_time', 'Response Time'),
        ('ssl_expiry', 'SSL Expiry'),
        ('custom', 'Custom'),
    ]

    ALERT_STATES = [
        ('pending', 'Pending'),
        ('triggered', 'Triggered'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]

    monitor = models.ForeignKey(
        Monitor,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES
    )
    state = models.CharField(
        max_length=15,
        choices=ALERT_STATES,
        default='pending'
    )
    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['monitor', '-triggered_at']),
            models.Index(fields=['state']),
        ]

    def __str__(self):
        return f"{self.monitor.name} - {self.alert_type} - {self.state}"


class AlertDelivery(models.Model):
    DELIVERY_METHODS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('inapp', 'In-App'),
    ]

    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
    ]

    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    method = models.CharField(
        max_length=10,
        choices=DELIVERY_METHODS
    )
    status = models.CharField(
        max_length=10,
        choices=DELIVERY_STATUS,
        default='pending'
    )
    recipient = models.CharField(max_length=255)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-sent_at'] if 'sent_at' else ['-id']
        indexes = [
            models.Index(fields=['alert', 'status']),
            models.Index(fields=['method']),
        ]
