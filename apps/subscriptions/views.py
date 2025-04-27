from django.shortcuts import render, redirect
from polar_sdk import Polar
from django.conf import settings
from .models import SubscriptionPlan, UserSubscription
from django.urls import reverse
from .forms import CancellationForm
from django.contrib import messages


# Create your views here.
def subscription(request):
    return render(request, 'subscription/failure.html')



def create_checkout_session(request, plan_type):
    plan = SubscriptionPlan.objects.get(plan_type=plan_type)

    with Polar(server="sandbox", access_token=settings.POLAR_API_KEY) as polar:
        # Create checkout using the proper request structure
        checkout = polar.checkouts.create(request={
            "products": [plan.polar_product_id],  # List of product IDs - required field
            "success_url": request.build_absolute_uri(reverse('subscriptions:subscription_success')) + "?checkout_id={CHECKOUT_ID}",
            "customer_email": request.user.email if request.user.is_authenticated else None,
            "customer_name": f"{request.user.first_name} {request.user.last_name}" if request.user.is_authenticated else None,
            "metadata": {
                "plan_type": plan_type,
                "user_id": str(request.user.id) if request.user.is_authenticated else None
            },
        })
        
    return redirect(checkout.url)


def subscription_success(request):
    checkout_id = request.GET.get('checkout_id')
    
    with Polar(access_token=settings.POLAR_API_KEY) as polar:
        try:
            # Use the get() method
            checkout = polar.checkouts.get(id=checkout_id)
            
            # Get the subscription details and create/update subscription
            if checkout and checkout.subscription_id:
                plan = SubscriptionPlan.objects.get(
                    polar_product_id=checkout.product.id
                )
                
                subscription, created = UserSubscription.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'plan': plan,
                        'polar_subscription_id': checkout.subscription_id,
                        'polar_customer_id': checkout.customer_id,
                        'active': True
                    }
                )
                
                messages.success(request, 'Your subscription has been activated successfully!')
            else:
                messages.error(request, 'Unable to process subscription. Please contact support.')
                
        except Exception as e:
            messages.error(request, f'Error processing subscription: {str(e)}')
            
    return redirect('subscriptions:subscription')


def cancel_subscription(request):
    if request.method == 'POST':
        form = CancellationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your subscription has been cancelled successfully.')
            return redirect('subscriptions:subscription')
        else:
            messages.error(request, 'There was an error cancelling your subscription.')
    return render(request, 'settings/partials/subscription.html')