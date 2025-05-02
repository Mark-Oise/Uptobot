from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from apps.subscriptions.models import UserSubscription
from apps.subscriptions.forms import CancellationForm
from .forms import CustomChangePasswordForm, UserAccountUpdateForm
from django.contrib.auth import update_session_auth_hash
# Create your views here.



# Create your views here.

def settings_view(request):
    if request.method == 'POST':

        if 'account_update' in request.POST:
            account_update_form = UserAccountUpdateForm(request.POST, instance=request.user)
            if account_update_form.is_valid():
                account_update_form.save()
                messages.success(request, 'Your account has been updated successfully.')
            else:
                messages.error(request, 'Please correct the errors below.')

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

        elif 'password_change' in request.POST:
            password_change_form = CustomChangePasswordForm(request.user, request.POST)
            if password_change_form.is_valid():
                password_change_form.save()

                # Update session to prevent logging out after password change
                update_session_auth_hash(request, request.user)
                
                messages.success(request, 'Password updated successfully.')
                return redirect('settings:settings')
            else:
                messages.error(request, 'Please correct the errors below.')

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