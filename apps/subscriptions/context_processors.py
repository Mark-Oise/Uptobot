from .models import SubscriptionPlan, UserSubscription
from django.contrib.auth.models import User

from django.shortcuts import render, redirect


def get_subscription_context(request):
    """Helper function to get subscription context data"""
    if request.user.is_authenticated:
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            plan = subscription.plan
            monitor_count = request.user.monitors.count()  # Assuming there's a monitors relation
            return {
                'subscription': subscription,
                'plan': plan,
                'monitor_count': monitor_count,
                'monitor_percentage': (monitor_count / plan.max_monitors * 100) if plan.max_monitors > 0 else 0
            }
        except UserSubscription.DoesNotExist:
            # Return default plan info if no subscription exists
            plan = SubscriptionPlan.get_default_plan()
            return {
                'subscription': None,
                'plan': plan,
                'monitor_count': 0,
                'monitor_percentage': 0
            }
    return {}