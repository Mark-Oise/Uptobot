from django.db import models
from django.conf import settings
from django.utils import timezone



class SubscriptionPlan(models.Model):
    PLAN_TYPES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=255)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    max_urls = models.IntegerField()
    min_interval = models.IntegerField(help_text='Minimum check interval in minutes')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    history_retention_days = models.IntegerField(default=7)
    
    def __str__(self):
        return f"{self.name} (${self.price}/month)"
    


class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"


    def checkout_success(self):
        self.active = True
        self.start_date = timezone.now()
        self.save()
    
    def checkout_cancel(self):
        self.active = False
        self.save()