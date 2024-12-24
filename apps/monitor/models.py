from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import ssl
import socket
import OpenSSL.SSL
from datetime import datetime
import OpenSSL.crypto
from urllib.parse import urlparse
import requests
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.urls import reverse


# Create your models here.


class Monitor(models.Model):
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

    last_ssl_check = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Last SSL certificate check timestamp'
    )
    ssl_expiry_date = models.DateTimeField(null=True, blank=True, help_text='SSL certificate expiry date')
    ssl_issuer = models.TextField(null=True, blank=True, help_text='SSL certificate issuer details')
    

    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        blank=True,
        help_text='URL-friendly identifier for the monitor'
    )
    
    def __str__(self):
        return f"{self.name} ({self.url})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Monitor'
        verbose_name_plural = 'Monitors'
        indexes = [
            models.Index(fields=['slug']),
        ]


    def get_uptime_percentage(self, days=30):
        """Calculate uptime percentage for the last n days"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all logs for the period
        logs = self.logs.filter(checked_at__range=(start_date, end_date))
        
        if not logs.exists():
            return None  # Return None instead of 0 for no data
        
        successful_checks = logs.filter(status='success').count()
        total_checks = logs.count()
        
        return round((successful_checks / total_checks) * 100, 2) if total_checks > 0 else None

    
    def get_average_response_time(self, days=30):
        """Calculate average response time for the last n days"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Use select_related to optimize query and add caching
        logs = self.logs.filter(
            checked_at__range=(start_date, end_date),
            status='success',
            response_time__isnull=False
        ).values('response_time')
        
        if not logs.exists():
            return None
        
        # Use database aggregation instead of Python calculation
        result = logs.aggregate(
            avg_time=models.Avg('response_time'),
            # Also get min and max for additional insights
            min_time=models.Min('response_time'),
            max_time=models.Max('response_time')
        )
        
        return round(result['avg_time'], 2) if result['avg_time'] is not None else None

    
    def get_ssl_certificate_info(self):
        """Get SSL certificate information using requests with proper connection handling"""
        if not self.url.startswith('https'):
            return {'valid': False, 'expiry_date': None, 'error': 'Not an HTTPS URL'}
        
        try:
            with requests.Session() as session:
                req = requests.Request('GET', self.url)
                prepped = session.prepare_request(req)
                
                with session.send(prepped, verify=True, timeout=10, stream=True) as response:
                    if not response.raw.connection or not response.raw.connection.sock:
                        return {
                            'valid': False,
                            'expiry_date': None,
                            'error': 'Could not establish secure connection'
                        }
                    
                    cert = response.raw.connection.sock.getpeercert()
                    
                    if not cert:
                        return {
                            'valid': False,
                            'expiry_date': None,
                            'error': 'No certificate provided'
                        }
                    
                    # Parse expiry date
                    expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    
                    # Extract organization name from issuer
                    issuer_dict = dict(x[0] for x in cert['issuer'])
                    organization_name = issuer_dict.get('organizationName', 'Unknown Issuer')
                    
                    return {
                        'valid': True,
                        'expiry_date': timezone.make_aware(expiry_date),
                        'issuer': organization_name,  # Now just returns the organization name
                        'error': None
                    }
                    
        except requests.exceptions.SSLError as e:
            return {
                'valid': False,
                'expiry_date': None,
                'error': f'SSL Certificate Invalid: {str(e)}'
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
        uptime = self.get_uptime_percentage(days=days)
        uptime_score = (uptime * 0.5) if uptime is not None else 0

        # Get response time score (0-30 points)
        avg_response_time = self.get_average_response_time(days=days)
        if avg_response_time is None:
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

    def save(self, *args, **kwargs):
        # Generate slug if it doesn't exist
        if not self.slug:
            self.slug = self.generate_unique_slug()
            
        # Check if this is a new monitor or if is_active changed from False to True
        is_new = not self.pk
        if not is_new:
            old_instance = Monitor.objects.get(pk=self.pk)
            was_reactivated = not old_instance.is_active and self.is_active
        else:
            was_reactivated = False

        super().save(*args, **kwargs)

        # Schedule immediate check for new or reactivated monitors
        if (is_new or was_reactivated) and self.is_active:
            from .tasks import check_monitor
            check_monitor.delay(self.id)


    def get_daily_uptime_history(self, days=5):
        """
        Get daily uptime percentages for the last n days
        Returns a list of dictionaries containing date and uptime percentage, most recent first
        """
        history = []
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)  # -1 because we want to include today
        
        # Iterate through dates in reverse order (newest to oldest)
        current_date = end_date
        while current_date >= start_date:
            # Get start and end of the day in timezone-aware datetime
            day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
            day_end = timezone.make_aware(datetime.combine(current_date, datetime.max.time()))
            
            # Get logs for the day
            daily_logs = self.logs.filter(
                checked_at__range=(day_start, day_end)
            )
            
            if daily_logs.exists():
                successful_checks = daily_logs.filter(status='success').count()
                total_checks = daily_logs.count()
                uptime = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
            else:
                uptime = None  # No data for this day
            
            history.append({
                'date': current_date,
                'uptime': uptime
            })
            
            current_date -= timedelta(days=1)
        
        return history
    
        
    def get_response_time_data(self, period='7d'):
        """Get response time data for different time periods"""
        end_date = timezone.now()
    
        # Define time periods
        if period == '1d':  # Today
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'yesterday':
            end_date = timezone.now().replace(hour=23, minute=59, second=59)
            start_date = end_date.replace(hour=0, minute=0, second=0) - timedelta(days=1)
        elif period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '14d':
            start_date = end_date - timedelta(days=14)
        else:
            raise ValueError("Invalid period")

        # Get logs for the period
        logs = self.logs.filter(
            checked_at__range=(start_date, end_date),
            status='success',
            response_time__isnull=False
        ).order_by('checked_at')

        # Group by date and calculate average
        data = logs.extra(
            select={'date': "DATE(checked_at)"}
        ).values('date').annotate(
            avg_response_time=models.Avg('response_time')
        ).order_by('date')

        return list(data)

    def generate_unique_slug(self):
        """Generate a unique slug with optional random suffix"""
        max_length = self._meta.get_field('slug').max_length
        base_slug = slugify(self.name)[:max_length - 8]  # Leave room for random suffix
        
        while True:
            slug = base_slug
            if not Monitor.objects.filter(slug=slug).exists():
                return slug
                
            # If slug exists, append random string
            suffix = get_random_string(4)
            slug = f"{base_slug}-{suffix}"
            if not Monitor.objects.filter(slug=slug).exists():
                return slug

    def get_absolute_url(self):
        return reverse('monitor:detail', kwargs={'slug': self.slug})



class MonitorLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('error', 'Error'),
        ('warning', 'Warning'),
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
            # Add new index for response time queries
            models.Index(fields=['status', 'response_time', 'checked_at']),
        ]

    def __str__(self):
        return f"{self.monitor} - {self.status} at {self.checked_at}"
