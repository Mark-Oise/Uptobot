from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import EmailValidator
from .managers import CustomUserManager
from uuid import uuid4

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
    email_alerts_enabled = models.BooleanField(default=True)
    sms_alerts_enabled = models.BooleanField(default=False)
    
    alert_frequency = models.CharField(
        max_length=10,
        choices=ALERT_FREQUENCY_CHOICES,
        default='immediate'
    )
    silent_hours_start = models.TimeField(null=True, blank=True)
    silent_hours_end = models.TimeField(null=True, blank=True)

    def toggle_email_alerts(self):
        self.email_alerts_enabled = not self.email_alerts_enabled
        self.save()

    def __str__(self):
        return f"{self.user.username}'s Alert settings"
