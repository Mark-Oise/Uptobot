from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import AccountUpdateForm, AlertSettingsForm
from .models import UserAlertSettings


# Create your views here.

def settings_view(request):
    # Get or create alert settings for the user
    alert_settings, created = UserAlertSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if 'alert_settings_form' in request.POST:
            alert_form = AlertSettingsForm(request.POST, instance=alert_settings)
            account_form = AccountUpdateForm(instance=request.user)
            if alert_form.is_valid():
                alert_form.save()
                messages.success(request, 'Account settings updated successfully.')
                return redirect('settings')
        else:
            alert_form = AlertSettingsForm(instance=alert_settings)
            account_form = AccountUpdateForm(request.POST, instance=request.user)
            if account_form.is_valid():
                account_form.save()
                messages.success(request, 'Alert settings updated successfully.')
                return redirect('settings')
    else:
        alert_form = AlertSettingsForm(instance=alert_settings)
        account_form = AccountUpdateForm(instance=request.user)

    context = {
        'form': account_form,
        'alert_form': alert_form,
    }
    return render(request, 'dashboard/monitor/settings.html', context)