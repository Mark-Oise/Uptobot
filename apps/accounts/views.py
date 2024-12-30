from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
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
            password_form = PasswordChangeForm(request.user)  # Add this
            if alert_form.is_valid():
                alert_form.save()
                messages.success(request, 'Alert settings updated successfully.')
                return redirect('accounts:settings')
        elif 'password_change_form' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            # Add these two lines
            account_form = UserAccountUpdateForm(instance=request.user)
            alert_form = UserAlertSettingsForm(instance=alert_settings)
            if password_form.is_valid():
                user = password_form.save()
                # Update session to prevent logging out after password change
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('accounts:settings')
            else:
                messages.error(request, 'Please correct the errors below.')
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
        password_form = PasswordChangeForm(request.user)

    context = {
        'account_form': account_form,  # Renamed to be more explicit
        'alert_form': alert_form,
        'password_form': password_form,  # Add password form to context
    }
    return render(request, 'dashboard/settings.html', context)