from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from .models import UserSubscription, SubscriptionPlan
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

@csrf_exempt
@require_POST
def handle_polar_webhook(request):
    """Handle Polar webhook events"""
    event = request.POST.get('event')
    data = request.POST.get('data')

    if not event or not data:
        return HttpResponse(status=400)

    try:
        if event == 'subscription.created':
            # Get user and plan from the webhook data
            user = User.objects.get(id=data['metadata']['user_id'])
            plan = SubscriptionPlan.objects.get(polar_product_id=data['product']['id'])
            
            # Create or update subscription
            UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'active': True,
                    'polar_subscription_id': data['subscription']['id'],
                    'polar_customer_id': data['customer']['id'],
                    'start_date': timezone.now(),
                    'end_date': None
                }
            )

        elif event == 'subscription.updated':
            subscription = UserSubscription.objects.get(
                polar_subscription_id=data['subscription']['id']
            )
            
            # Update plan if changed
            new_plan = SubscriptionPlan.objects.get(polar_product_id=data['product']['id'])
            subscription.plan = new_plan
            subscription.active = True
            
            if data.get('current_period_end'):
                subscription.end_date = data['current_period_end']
                
            subscription.save()

        elif event == 'subscription.cancelled':
            subscription = UserSubscription.objects.get(
                polar_subscription_id=data['subscription']['id']
            )
            subscription.active = False
            subscription.end_date = timezone.now()
            subscription.save()

        elif event == 'subscription.payment_failed':
            subscription = UserSubscription.objects.get(
                polar_subscription_id=data['subscription']['id']
            )
            subscription.active = False
            subscription.save()

            # Notify user about failed payment
            send_mail(
                'Payment Failed - Action Required',
                'Your subscription payment has failed. Please update your payment method to continue service.',
                settings.DEFAULT_FROM_EMAIL,
                [subscription.user.email],
                fail_silently=True,
            )

        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(str(e), status=400)