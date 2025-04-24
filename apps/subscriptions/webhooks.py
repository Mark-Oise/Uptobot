from django.http import HttpResponse
from polar_sdk import Polar
from .models import UserSubscription, SubscriptionPlan
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def handle_polar_webhook(request):
    """Handle Polar webhook events"""
    event = request.POST.get('event')
    data = request.POST.get('data')

    if event == 'subscription.created':
        # New subscription created
        user = User.objects.get(email=data['customer']['email'])
        plan = SubscriptionPlan.objects.get(polar_product_id=data['product']['id'])
        
        UserSubscription.create_from_polar(
            user=user,
            plan=plan,
            polar_subscription_id=data['subscription']['id'],
            polar_customer_id=data['customer']['id']
        )

    elif event == 'subscription.updated':
        # Subscription updated (e.g., plan change)
        subscription = UserSubscription.objects.get(
            polar_subscription_id=data['subscription']['id']
        )
        plan = SubscriptionPlan.objects.get(polar_product_id=data['product']['id'])
        
        subscription.plan = plan
        subscription.save()
        
        # Sync the latest status
        with Polar(access_token=settings.POLAR_API_KEY) as polar:
            subscription.sync_with_polar(polar)

    elif event == 'subscription.cancelled':
        # Subscription cancelled
        subscription = UserSubscription.objects.get(
            polar_subscription_id=data['subscription']['id']
        )
        subscription.checkout_cancel()

    elif event == 'subscription.payment_failed':
        subscription = UserSubscription.objects.get(
            polar_subscription_id=data['subscription']['id']
        )
        # Handle failed payment (e.g., notify user)
        subscription.active = False
        subscription.save()

    return HttpResponse(status=200)