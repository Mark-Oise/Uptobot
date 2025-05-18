from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from apps.subscriptions.models import UserSubscription
from apps.subscriptions.forms import CancellationForm
from apps.accounts.forms import NotificationChannelForm
from .forms import CustomChangePasswordForm, UserAccountUpdateForm
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.urls import reverse
import requests
from apps.accounts.models import UserNotificationChannel
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Create your views here.


@login_required
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


    # Get all subscriptions for the user, ordered by start date
    subscriptions = UserSubscription.objects.filter(user=request.user).order_by('-start_date')
    current_subscription = subscriptions.filter(active=True).first()

    # Get notification channels
    notification_channels = {
        channel.channel: channel
        for channel in UserNotificationChannel.objects.filter(user=request.user)
    }

    context = {
        'current_subscription': current_subscription,
        'subscriptions': subscriptions,
        'cancellation_form': CancellationForm(),
        'notification_channels': notification_channels,
    }
    return render(request, 'settings/settings.html', context)



@login_required
def slack_oauth_connect(request):
    """Initiate Slack OAuth flow"""
    redirect_uri = 'https://e4bf-197-211-59-59.ngrok-free.app/slack/callback/'
    
    return redirect(
        f'https://slack.com/oauth/v2/authorize?'
        f'client_id={settings.SLACK_CLIENT_ID}&'
        f'scope=chat:write,chat:write.public,incoming-webhook&'
        f'redirect_uri={redirect_uri}'
    )

@login_required
def slack_oauth_callback(request):
    """Handle Slack OAuth callback"""
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Slack integration failed')
        return redirect('settings:settings')

    redirect_uri = 'https://e4bf-197-211-59-59.ngrok-free.app/slack/callback/'

    # Exchange code for access token
    response = requests.post('https://slack.com/api/oauth.v2.access', data={
        'client_id': settings.SLACK_CLIENT_ID,
        'client_secret': settings.SLACK_CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri
    })
    
    data = response.json()
    if data.get('ok', False):
        team = data.get('team', {})
        incoming_webhook = data.get('incoming_webhook', {})
        
        if not incoming_webhook:
            messages.error(request, 'No channel was selected. Please try again and select a channel.')
            return redirect('settings:settings')
        
        # Check if this is a channel change
        is_channel_change = request.session.pop('slack_channel_change', False)
        
        UserNotificationChannel.objects.update_or_create(
            user=request.user,
            channel='slack',
            defaults={
                'oauth_token': data['access_token'],
                'channel_id': incoming_webhook.get('channel_id'),
                'workspace_name': team.get('name'),
                'channel_name': incoming_webhook.get('channel'),
                'workspace_icon': team.get('icon', {}).get('image_132'),
                'enabled': True
            }
        )
        
        if is_channel_change:
            messages.success(request, f'Slack channel changed successfully to {incoming_webhook.get("channel")}')
        else:
            messages.success(request, f'Slack connected successfully to channel {incoming_webhook.get("channel")}')
    else:
        messages.error(request, f'Failed to connect Slack: {data.get("error", "Unknown error")}')
    
    return redirect('settings:settings')


@login_required
def discord_oauth_connect(request):
    """Initiate Discord OAuth flow"""
    return redirect(
        f'https://discord.com/api/oauth2/authorize?'
        f'client_id={settings.DISCORD_CLIENT_ID}&'
        f'scope=messages.read&'  # Minimal scope needed
        f'response_type=code&'
        f'redirect_uri={request.build_absolute_uri(reverse("discord_oauth_callback"))}'
    )


@login_required
def discord_oauth_callback(request):
    """Handle Discord OAuth callback"""
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Discord integration failed')
        return redirect('settings_notifications')

    response = requests.post('https://discord.com/api/oauth2/token', data={
        'client_id': settings.DISCORD_CLIENT_ID,
        'client_secret': settings.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': request.build_absolute_uri(reverse("discord_oauth_callback"))
    })
    
    if response.ok:
        data = response.json()
        UserNotificationChannel.objects.update_or_create(
            user=request.user,
            channel='discord',
            defaults={
                'oauth_token': data['access_token'],
                'enabled': True
            }
        )
        messages.success(request, 'Discord connected successfully')
    else:
        messages.error(request, 'Failed to connect Discord')
    
    return redirect('settings_notifications')

@login_required
def slack_change_channel(request):
    """Initiate Slack OAuth flow for channel change"""
    # Get existing slack connection
    slack_connection = UserNotificationChannel.objects.filter(
        user=request.user,
        channel='slack'
    ).first()
    
    if not slack_connection:
        messages.error(request, 'No Slack connection found')
        return redirect('settings:settings')
    
    redirect_uri = 'https://e4bf-197-211-59-59.ngrok-free.app/slack/callback/'
    
    # Use the same OAuth flow but store a session flag to indicate it's a channel change
    request.session['slack_channel_change'] = True
    
    return redirect(
        f'https://slack.com/oauth/v2/authorize?'
        f'client_id={settings.SLACK_CLIENT_ID}&'
        f'scope=chat:write,chat:write.public,incoming-webhook&'
        f'redirect_uri={redirect_uri}'
    )

@login_required
def slack_disconnect(request):
    """Disconnect Slack integration"""
    try:
        slack_connection = UserNotificationChannel.objects.get(
            user=request.user,
            channel='slack'
        )
        # Instead of deleting, clear Slack-specific fields and disable
        slack_connection.oauth_token = None
        slack_connection.channel_id = None
        slack_connection.workspace_name = None
        slack_connection.channel_name = None
        slack_connection.workspace_icon = None
        slack_connection.save()
        
        messages.success(request, 'Slack disconnected successfully')
    except UserNotificationChannel.DoesNotExist:
        messages.error(request, 'No Slack connection found')
    
    return redirect('settings:settings')