from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import ssl
import socket
import OpenSSL.SSL
from urllib.parse import urlparse


# Create your models here.


class Monitor(models.Model):
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
    url = models.URLField(max_length=255, help_text='URL to monitor')
    method = models.CharField(max_length=6, choices=METHOD_CHOICES, default='GET', help_text='HTTP method')
    interval = models.IntegerField(choices=INTERVAL_CHOICES, default=5, help_text='Monitoring interval in minutes')
    
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
        return f"{self.name} ({self.url})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Monitor'
        verbose_name_plural = 'Monitors'


    def get_uptime_percentage(self, days=30):
        """Calculate uptime percentage for the last n days"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all logs for the period
        logs = self.logs.filter(checked_at__range=(start_date, end_date))
        
        if not logs.exists():
            return 0
        
        successful_checks = logs.filter(status='success').count()
        total_checks = logs.count()
        
        return round((successful_checks / total_checks) * 100, 2) if total_checks > 0 else 0

    def get_average_response_time(self, days=30):
        """Calculate average response time for the last n days"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get successful logs with response times
        logs = self.logs.filter(
            checked_at__range=(start_date, end_date),
            status='success',
            response_time__isnull=False
        )
        
        if not logs.exists():
            return 0
            
        return round(logs.aggregate(avg_time=models.Avg('response_time'))['avg_time'], 2)

    def get_ssl_info(self):
        """Get SSL certificate information"""
        if not self.url.startswith('https'):
            return {'valid': False, 'expiry_date': None, 'error': 'Not an HTTPS URL'}
            
        try:
            hostname = urlparse(self.url).netloc
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    not_after = ssl.cert_time_to_seconds(cert['notAfter'])
                    expiry_date = timezone.datetime.fromtimestamp(not_after)
                    
                    return {
                        'valid': True,
                        'expiry_date': expiry_date,
                        'error': None
                    }
        except Exception as e:
            return {
                'valid': False,
                'expiry_date': None,
                'error': str(e)
            }

    def get_health_score(self, days=7):
        """
        Calculate health score (0-100) based on:
        - Uptime percentage (50% of score)
        - Response time performance (30% of score)
        - Recent failures (20% of score)
        """
        # Get uptime score (0-50 points)
        uptime_score = self.get_uptime_percentage(days=days) * 0.5

        # Get response time score (0-30 points)
        avg_response_time = self.get_average_response_time(days=days)
        if avg_response_time == 0:
            response_time_score = 0
        else:
            # Assuming response times under 500ms are ideal
            # Score decreases linearly until 2000ms (2 seconds)
            response_time_score = max(0, 30 * (1 - (avg_response_time - 500) / 1500))
            response_time_score = min(30, response_time_score)  # Cap at 30 points

        # Get recent failures score (0-20 points)
        recent_failures = self.logs.filter(
            status__in=['failure', 'error'],
            checked_at__gte=timezone.now() - timedelta(days=days)
        ).count()
        
        # Deduct points for each failure (max 20 points deduction)
        failure_deduction = min(20, recent_failures * 4)  # 4 points per failure
        failure_score = 20 - failure_deduction

        # Calculate total score
        total_score = uptime_score + response_time_score + failure_score
        
        return round(total_score, 1)

    def get_health_status(self):
        """
        Returns a tuple of (status, color) based on health score
        """
        score = self.get_health_score()
        if score >= 90:
            return ('Excellent', 'green')
        elif score >= 75:
            return ('Good', 'blue')
        elif score >= 50:
            return ('Fair', 'yellow')
        else:
            return ('Poor', 'red')


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
