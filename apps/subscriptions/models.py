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
        if not self.allowed_notification_channels:
            return []
        # Return as a simple list of channel names
        return list(self.allowed_notification_channels)

    def __str__(self):
        return f"{self.name} (${self.price}/month)"
    


class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Add Polar-specific fields
    polar_subscription_id = models.CharField(max_length=255, null=True)
    polar_customer_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    @classmethod
    def create_from_polar(cls, user, plan, polar_subscription_id, polar_customer_id):
        """Create a subscription from Polar webhook data"""
        subscription = cls.objects.create(
            user=user,
            plan=plan,
            polar_subscription_id=polar_subscription_id,
            polar_customer_id=polar_customer_id,
            active=True,
            start_date=timezone.now()
        )
        return subscription

    def sync_with_polar(self, polar_client):
        """Sync subscription status with Polar"""
        if self.polar_subscription_id:
            try:
                polar_sub = polar_client.subscriptions.get(self.polar_subscription_id)
                self.active = polar_sub.status == 'active'
                self.end_date = polar_sub.current_period_end
                self.save()
            except Exception as e:
                # Log the error but don't raise it
                logger.error(f"Failed to sync subscription with Polar: {e}")


    def checkout_success(self, polar_subscription_id, polar_customer_id):
        """Handle successful checkout"""
        self.active = True
        self.start_date = timezone.now()
        self.polar_subscription_id = polar_subscription_id
        self.polar_customer_id = polar_customer_id
        self.save()
    
    
    def checkout_cancel(self):
        """Handle subscription cancellation"""
        self.active = False
        self.end_date = timezone.now()
        self.save()

        # Cancel in Polar if we have a subscription ID
        if self.polar_subscription_id:
            try:
                with Polar(access_token=settings.POLAR_API_KEY) as polar:
                    polar.subscriptions.cancel(self.polar_subscription_id)
            except Exception as e:
                logger.error(f"Failed to cancel Polar subscription: {e}")


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
