from django.db import models
from django.conf import settings
from apps.monitor.models import Monitor

class Alert(models.Model):
    ALERT_TYPES = [
        ('monitor_down', 'Monitor Down'),
        ('monitor_up', 'Monitor Up'),
        ('availability', 'Availability Issue'),
        ('response_time', 'Response Time Threshold'),
        ('latency_spike', 'Latency Spike'),
        ('ssl_expiring_soon', 'SSL Certificate Expiring Soon'),
        ('ssl_expired', 'SSL Certificate Expired'),
        ('ssl_invalid', 'SSL Certificate Invalid'),
    ]

    SEVERITY_LEVELS = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Information'),
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
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='warning'
    )
    message = models.TextField()
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['monitor', '-created_at']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['severity']),
        ]

    def __str__(self):
        return f"{self.monitor.name} - {self.get_alert_type_display()}"


class AlertDelivery(models.Model):
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    status = models.CharField(
        max_length=10,
        choices=DELIVERY_STATUS,
        default='pending'
    )
    recipient = models.EmailField()
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-sent_at'] if 'sent_at' else ['-id']
        indexes = [
            models.Index(fields=['alert', 'status']),
        ]
