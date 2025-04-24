from functools import wraps
from django.core.exceptions import PermissionDenied

def check_subscription_limits(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'subscription'):
            # Redirect to subscription page or return error
            raise PermissionDenied("No active subscription")
            
        subscription = user.subscription
        plan = subscription.plan

        # Check if action is allowed based on subscription
        if 'monitor' in kwargs:
            current_monitor_count = user.monitors.count()
            if not plan.can_add_monitor(current_monitor_count):
                raise PermissionDenied(f"Your {plan.name} plan is limited to {plan.max_monitors} monitors")

        return view_func(request, *args, **kwargs)
    return wrapper
