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
    

class UserNotificationChannel(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('discord', 'Discord'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_channels')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    enabled = models.BooleanField(default=True)
    oauth_token = models.CharField(max_length=255, blank=True, null=True)
    channel_id = models.CharField(max_length=100, blank=True, null=True)
    workspace_name = models.CharField(max_length=255, blank=True, null=True)
    channel_name = models.CharField(max_length=255, blank=True, null=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    workspace_icon = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'channel')

    def __str__(self):
        return f"{self.user.username} - {self.channel} ({'enabled' if self.enabled else 'disabled'})"

