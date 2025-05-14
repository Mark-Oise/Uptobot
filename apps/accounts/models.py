from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import EmailValidator
from .managers import CustomUserManager
from uuid import uuid4
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    public_id = models.UUIDField(default=uuid4, editable=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class UserAlertSettings(models.Model):
    ALERT_FREQUENCY_CHOICES = [
        ('immediate', 'Immediate'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alert_frequency = models.CharField(
        max_length=10,
        choices=ALERT_FREQUENCY_CHOICES,
        default='immediate'
    )
    silent_hours_start = models.TimeField(null=True, blank=True)
    silent_hours_end = models.TimeField(null=True, blank=True)
    last_alert_sent = models.DateTimeField(null=True, blank=True)

    def can_receive_alerts(self):
        now = timezone.now()
        current_time = now.time()

        # Check if user has at least one enabled notification channel
        if not self.user.notification_channels.filter(enabled=True).exists():
            return False

        # Silent hours logic (handles cases that span midnight)
        if self.silent_hours_start and self.silent_hours_end:
            if self.silent_hours_start < self.silent_hours_end:
                # Silent hours in the same day
                if self.silent_hours_start <= current_time <= self.silent_hours_end:
                    return False
            else:
                # Silent hours span across midnight
                if current_time >= self.silent_hours_start or current_time <= self.silent_hours_end:
                    return False

        # Frequency rules
        if self.alert_frequency == 'immediate':
            return True

        if self.last_alert_sent:
            if self.alert_frequency == 'daily':
                return (now - self.last_alert_sent) >= timedelta(days=1)
            elif self.alert_frequency == 'weekly':
                return (now - self.last_alert_sent) >= timedelta(weeks=1)

        # If no alerts have ever been sent, allow sending
        return True

    def __str__(self):
        return f"{self.user.username}'s Alert settings"
    

class UserNotificationChannel(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('discord', 'Discord'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_channels')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    enabled = models.BooleanField(default=True)
    webhook_url = models.URLField(blank=True, null=True)  # For Slack or Discord
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # For SMS, optional

    class Meta:
        unique_together = ('user', 'channel')

    def __str__(self):
        return f"{self.user.username} - {self.channel} ({'enabled' if self.enabled else 'disabled'})"

