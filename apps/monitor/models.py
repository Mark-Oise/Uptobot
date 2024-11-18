from django.db import models
from django.conf import settings


# Create your models here.


class Monitor(models.Model):
    # Protocol choices
    PROTOCOL_CHOICES = [
        ('HTTP', 'HTTP'),
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
    ]

    # Interval choices in minutes
    INTERVAL_CHOICES = [
        (5, '5 minutes'),
        (15, '15 minutes'),
        (30, '30 minutes'),
        ('custom', 'Custom'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='monitors')
    url = models.CharField(max_length=255, )
    protocol = models.CharField(max_length=4, choices=PROTOCOL_CHOICES, default='HTTP',
                                help_text='Protocol to monitor.')
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES, default=5, help_text='Monitoring interval.')
    custom_interval = models.PositiveIntegerField(null=True, blank=True, help_text='Custom interval in minutes.')
    alert_threshold = models.PositiveIntegerField(default=3, help_text='Failures before alert is triggered.')
    last_checked = models.DateTimeField(null=True, blank=True, help_text='Last check timestamp.')
    is_online = models.BooleanField(default=True, help_text='Monitor active status.')

    created_at = models.DateTimeField(auto_now_add=True, help_text='Timestamp of creation.')
    updated_at = models.DateTimeField(auto_now=True, help_text='Timestamp of last update.')

    def __str__(self):
        return f"{self.url} ({self.protocol})"


    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Monitor'
        verbose_name_plural = 'Monitors'


class MonitorLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('error', 'Error'),
    ]

    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, related_name='logs', 
                              help_text='Associated monitor')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, 
                            help_text='Result status of the check')
    response_time = models.FloatField(null=True, blank=True,
                                    help_text='Response time in milliseconds')
    status_code = models.PositiveSmallIntegerField(null=True, blank=True,
                                                 help_text='HTTP status code (for HTTP monitors)')
    error_message = models.TextField(null=True, blank=True,
                                   help_text='Error details if check failed')
    checked_at = models.DateTimeField(auto_now_add=True,
                                    help_text='When the check was performed')

    class Meta:
        ordering = ['-checked_at']
        verbose_name = 'Monitor Log'
        verbose_name_plural = 'Monitor Logs'
        indexes = [
            models.Index(fields=['monitor', 'checked_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.monitor} - {self.status} at {self.checked_at}"
