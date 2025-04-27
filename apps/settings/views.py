from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from apps.subscriptions.models import UserSubscription
from apps.subscriptions.forms import CancellationForm
# Create your views here.



# Create your views here.

def settings_view(request):
    if request.method == 'POST':
        if 'cancel_subscription' in request.POST:
            current_subscription = UserSubscription.objects.filter(
                user=request.user, 
                active=True
            ).first()
            
            if current_subscription:
                cancellation_form = CancellationForm(
                    data=request.POST,
                    subscription=current_subscription
                )
                if cancellation_form.is_valid():
                    cancellation_form.save()
                    current_subscription.checkout_cancel()
                    messages.success(request, 'Your subscription has been cancelled successfully.')
                    return redirect('settings:settings')
            
            messages.error(request, 'There was an error cancelling your subscription.')
        return redirect('settings:settings')

    # Get all subscriptions for the user, ordered by start date
    subscriptions = UserSubscription.objects.filter(user=request.user).order_by('-start_date')
    current_subscription = subscriptions.filter(active=True).first()

    context = {
        'current_subscription': current_subscription,
        'subscriptions': subscriptions,
        'cancellation_form': CancellationForm(),
    }
    return render(request, 'settings/settings.html', context)