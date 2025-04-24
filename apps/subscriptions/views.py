from django.shortcuts import render, redirect
from polar_sdk import Polar
from django.conf import settings
from django.http import JsonResponse
from .models import SubscriptionPlan, UserSubscription
from django.urls import reverse

# Create your views here.
def subscription(request):
    return render(request, 'dashboard/subscription.html')




def create_checkout_session(request, plan_type):
    plan = SubscriptionPlan.objects.get(plan_type=plan_type)
    
    with Polar(access_token=settings.POLAR_API_KEY) as polar:
        # Changed from dict parameter to named arguments
        checkout = polar.checkouts.create(request={
            
        })
        
    return JsonResponse({
        'checkout_url': checkout.url
    })

def subscription_success(request):
    checkout_id = request.GET.get('checkout_id')
    
    with Polar(access_token=settings.POLAR_API_KEY) as polar:
        # Fetch the checkout session to get subscription details
        checkout = polar.checkouts.get(checkout_id)
        
        # Update the user's subscription
        subscription = UserSubscription.objects.get_or_create(
            user=request.user,
            defaults={
                'plan': SubscriptionPlan.objects.get(
                    polar_product_id=checkout.products[0]
                ),
                'polar_subscription_id': checkout.subscription_id,
                'active': True
            }
        )
        
    return redirect('subscriptions:subscription')