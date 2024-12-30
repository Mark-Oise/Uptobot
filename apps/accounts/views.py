from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserAccountUpdateForm, UserAlertSettingsForm
from .models import UserAlertSettings


# Create your views here.

def settings_view(request):
     # Get the alert settings for the current user
    alert_settings = UserAlertSettings.objects.get(user=request.user)
    
    if request.method == 'POST':
        if 'alert_settings_form' in request.POST:
            alert_form = UserAlertSettingsForm(request.POST, instance=alert_settings)
            account_form = UserAccountUpdateForm(instance=request.user)
            if alert_form.is_valid():
                alert_form.save()
                messages.success(request, 'Alert settings updated successfully.')
                return redirect('accounts:settings')
        else:
            account_form = UserAccountUpdateForm(request.POST, instance=request.user)
            alert_form = UserAlertSettingsForm(instance=alert_settings)
            if account_form.is_valid():
                account_form.save()
                messages.success(request, 'Account settings updated successfully.')
                return redirect('accounts:settings')
    else:
        alert_form = UserAlertSettingsForm(instance=alert_settings)
        account_form = UserAccountUpdateForm(instance=request.user)

    context = {
        'account_form': account_form,  # Renamed to be more explicit
        'alert_form': alert_form,
    }
    return render(request, 'dashboard/settings.html', context)