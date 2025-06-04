from django.db import models
from django.conf import settings
from django.utils import timezone
from polar_sdk import Polar
import logging

logger = logging.getLogger(__name__)



class SubscriptionPlan(models.Model):
    PLAN_TYPES = [
        ('starter', 'Starter'),
        ('builder', 'Builder'),
        ('pro', 'Pro'),
    ]

    name = models.CharField(max_length=255)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    polar_product_id = models.CharField(max_length=255, unique=True, null=True)
    
    # Plan limits
    max_monitors = models.IntegerField()
    check_interval = models.IntegerField(help_text='Check interval in minutes')
    allowed_notification_channels = models.JSONField(default=list)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    @classmethod
    def get_default_plan(cls):
        return cls.objects.get(plan_type='starter')

    def can_add_monitor(self, current_monitor_count):
        return current_monitor_count < self.max_monitors

    def get_allowed_channels(self):
        """Get allowed notification channels based on plan type"""
        channel_mapping = {
            'starter': ['email'],
            'builder': ['email', 'discord'], 
            'pro': ['email', 'discord', 'slack']
        }
        return channel_mapping.get(self.plan_type, ['email'])

    def __str__(self):
        return f"{self.name} (${self.price}/month)"
    


class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    polar_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    polar_customer_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    @property
    def is_active(self):
        """Check if subscription is active and not expired"""
        if not self.active:
            return False
        if self.end_date and self.end_date < timezone.now():
            return False
        return True

    @classmethod
    def create_from_polar(cls, user, plan, polar_subscription_id, polar_customer_id):
        """Create a new subscription from Polar checkout data"""
        return cls.objects.create(
            user=user,
            plan=plan,
            polar_subscription_id=polar_subscription_id,
            polar_customer_id=polar_customer_id,
            active=True,
            start_date=timezone.now()
        )

    def can_add_monitor(self):
        """Check if user can add more monitors"""
        current_monitor_count = self.user.monitors.count()
        return current_monitor_count < self.plan.max_monitors

    def get_allowed_channels(self):
        """Get list of notification channels available for this subscription"""
        return self.plan.allowed_notification_channels

    def update_plan(self, new_plan):
        """Update subscription to a new plan"""
        self.plan = new_plan
        self.save()
        return self

    def cancel(self):
        """Cancel the subscription"""
        self.active = False
        self.end_date = timezone.now()
        self.save()

        # Attempt to cancel in Polar if subscription ID exists
        if self.polar_subscription_id and settings.POLAR_API_KEY:
            try:
                polar = Polar(access_token=settings.POLAR_API_KEY)
                polar.subscriptions.cancel(self.polar_subscription_id)
                return True
            except Exception:
                return False
        return True

    def reactivate(self):
        """Reactivate a cancelled subscription"""
        if not self.end_date or self.end_date > timezone.now():
            self.active = True
            self.end_date = None
            self.save()
            return True
        return False

    def get_usage(self):
        """Get current subscription usage stats"""
        return {
            'monitors': {
                'used': self.user.monitors.count(),
                'total': self.plan.max_monitors,
                'percentage': (self.user.monitors.count() / self.plan.max_monitors) * 100
            },
            'check_interval': self.plan.check_interval,
            'channels': self.get_allowed_channels()
        }

    def days_until_renewal(self):
        """Get number of days until subscription renews"""
        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return None

    def is_trialing(self):
        """Check if subscription is in trial period"""
        if not self.start_date:
            return False
        trial_days = 14  # Adjust trial period as needed
        trial_end = self.start_date + timezone.timedelta(days=trial_days)
        return timezone.now() <= trial_end


class CancellationReason(models.Model):
    REASON_CHOICES = [
        ('too_expensive', 'Too expensive'),
        ('not_using', 'Not using enough'),
        ('missing_features', 'Missing features'),
        ('technical_issues', 'Technical issues'),
        ('switching_service', 'Switching to another service'),
        ('other', 'Other'),
    ]

    subscription = models.OneToOneField(UserSubscription, on_delete=models.CASCADE, related_name='cancellation_reason')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subscription.user.email} - {self.reason}"
