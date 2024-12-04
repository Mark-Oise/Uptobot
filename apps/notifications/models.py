from django.db import models
from django.conf import settings
from apps.monitor.models import Monitor
from django.utils import timezone


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('monitor_down', 'Monitor Down'),
        ('monitor_up', 'Monitor Up'),
        ('alert_threshold', 'Alert Threshold Reached'),
        ('system', 'System Notification'),
    ]

    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='info'
    )
    monitor = models.ForeignKey(
        Monitor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    @classmethod
    def get_unread_count(cls, user):
        return cls.objects.filter(user=user, is_read=False).count()