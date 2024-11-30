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

    # HTTP Method choices
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]

    # Interval choices in minutes
    INTERVAL_CHOICES = [
        (5, '5 minutes'),
        (10, '10 minutes'),
        (15, '15 minutes'),
        (30, '30 minutes'),
        (60, '60 minutes'),
    ]

    # Status choices
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('unknown', 'Unknown'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='monitors')
    name = models.CharField(max_length=255, help_text='Monitor name')
    protocol = models.CharField(max_length=4, choices=PROTOCOL_CHOICES, default='HTTP',
                                help_text='Protocol to monitor.')
    interval = models.IntegerField(choices=INTERVAL_CHOICES, default=5, help_text='Monitoring interval in minutes.')
    
    # Fields specific to HTTP
    url = models.CharField(max_length=255, blank=True, null=True, help_text='URL to monitor.')
    method = models.CharField(max_length=6, choices=METHOD_CHOICES, blank=True, null=True, help_text='HTTP method.')

    # Fields specific to TCP/UDP
    host = models.CharField(max_length=255, blank=True, null=True, help_text='Host address.')
    port = models.PositiveIntegerField(blank=True, null=True, help_text='Port number.')

    description = models.TextField(blank=True, null=True, help_text='Description of the monitor.')
    alert_threshold = models.PositiveIntegerField(default=3, help_text='Failures before alert is triggered.')
    last_checked = models.DateTimeField(null=True, blank=True, help_text='Last check timestamp.')
    is_active = models.BooleanField(default=True, help_text='Whether monitoring is active or paused.')

    created_at = models.DateTimeField(auto_now_add=True, help_text='Timestamp of creation.')
    updated_at = models.DateTimeField(auto_now=True, help_text='Timestamp of last update.')

    availability = models.CharField(
        max_length=7,
        choices=STATUS_CHOICES,
        default='unknown',
        help_text='Current availability status of the monitored service.'
    )
    consecutive_failures = models.PositiveIntegerField(
        default=0,
        help_text='Number of consecutive failed checks.'
    )

    def __str__(self):
        return f"{self.name} ({self.protocol})"

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
