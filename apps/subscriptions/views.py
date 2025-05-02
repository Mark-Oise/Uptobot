from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from polar_sdk import Polar
from django.conf import settings
from .models import SubscriptionPlan, UserSubscription
from .forms import CancellationForm


# Create your views here.
def subscription(request):
    return render(request, 'subscription/subscription.html')


@login_required
def create_checkout_session(request, plan_type):
    """Create a checkout session for the selected plan"""
    try:
        plan = SubscriptionPlan.objects.get(plan_type=plan_type)
        
        polar = Polar(server="sandbox",access_token=settings.POLAR_API_KEY)
        checkout = polar.checkouts.create(request={
            "products": [plan.polar_product_id],
            "success_url": request.build_absolute_uri(reverse('subscriptions:subscription_success')),
            "customer_email": request.user.email,
            "metadata": {
                "user_id": str(request.user.id),
                "plan_type": plan_type
            }
        })
        
        return redirect(checkout.url)
        
    except Exception as e:
        messages.error(request, "Unable to create checkout session. Please try again.")
        return redirect('subscriptions:subscription')



@login_required
def subscription_success(request):
    """Handle successful subscription"""
    try:
        # Get the user's subscription
        subscription = request.user.subscription
        
        # Format dates for display
        start_date = subscription.start_date.strftime('%m/%d/%Y')
        next_billing = subscription.end_date.strftime('%m/%d/%Y') if subscription.end_date else None
        
        context = {
            'subscription': subscription,
            'plan': subscription.plan,
            'start_date': start_date,
            'next_billing': next_billing,
            # Generate a simple transaction ID (you might want to store this in your model)
            'transaction_id': f"TXN-{subscription.polar_subscription_id[:8].upper()}"
        }
        
        messages.success(request, "Your subscription has been activated successfully!")
        return render(request, 'subscription/success.html', context)
        
    except Exception as e:
        messages.error(request, "Unable to load subscription details. Please contact support.")
        return redirect('subscriptions:subscription')


@login_required
def subscription_failure(request):
    """Handle failed subscription"""
    messages.error(request, "Unable to process subscription. Please contact support.")
    return render(request, 'subscription/failure.html')


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