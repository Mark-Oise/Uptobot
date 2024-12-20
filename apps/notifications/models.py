from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('monitor_down', 'Monitor Down'),
        ('monitor_up', 'Monitor Up'),
        ('ssl_expiring', 'SSL Certificate Expiring'),
        ('response_time', 'Response Time Alert'),
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
        choices=NOTIFICATION_TYPES,
        db_index=True
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='info',
        db_index=True
    )
    monitor = models.ForeignKey(
        'monitor.Monitor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    @classmethod
    def mark_all_as_read(cls, user):
        return cls.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )

    @classmethod
    def get_unread_count(cls, user):
        return cls.objects.filter(user=user, is_read=False).count()


    def get_absolute_url(self):
        if self.action_url:
            return self.action_url
        if self.monitor:
            return reverse('monitor:monitor_detail', kwargs={'slug': self.monitor.slug})
        return reverse('notifications:list')