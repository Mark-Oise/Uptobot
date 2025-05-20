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
import json
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

    # Get notification channels and parse JSON details
    notification_channels = {
        channel.channel: {
            **channel.__dict__,
            'details': json.loads(channel.details) if channel.details else {}
        }
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
    return redirect(
        f'https://slack.com/oauth/v2/authorize?'
        f'client_id={settings.SLACK_CLIENT_ID}&'
        f'scope=chat:write,chat:write.public,incoming-webhook,team:read&'
        f'redirect_uri={settings.SLACK_REDIRECT_URI}'
    )

@login_required
def slack_oauth_callback(request):
    """Handle Slack OAuth callback"""
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Slack integration failed')
        return redirect('settings:settings')

    # Exchange code for access token
    response = requests.post('https://slack.com/api/oauth.v2.access', data={
        'client_id': settings.SLACK_CLIENT_ID,
        'client_secret': settings.SLACK_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.SLACK_REDIRECT_URI
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
                'workspace_icon': team.get('icon', {}).get('image_132') or team.get('image_132') or None,
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
    
    # Use the same OAuth flow but store a session flag to indicate it's a channel change
    request.session['slack_channel_change'] = True
    
    return redirect(
        f'https://slack.com/oauth/v2/authorize?'
        f'client_id={settings.SLACK_CLIENT_ID}&'
        f'scope=chat:write,chat:write.public,incoming-webhook&'
        f'redirect_uri={settings.SLACK_REDIRECT_URI}'
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



@login_required
def discord_oauth_connect(request):
    """Redirect user to Discord OAuth authorization page"""
    
    # Create Discord OAuth URL using the predefined redirect URI
    oauth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={settings.DISCORD_CLIENT_ID}"
        f"&redirect_uri={settings.DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify%20bot%20applications.commands"
        f"&permissions=2147483648"  # Permissions integer for your bot
    )
    
    return redirect(oauth_url)

@login_required
def discord_oauth_callback(request):
    """Handle Discord OAuth callback"""
    code = request.GET.get('code')
    if not code:
        messages.error(request, "Failed to connect to Discord")
        return redirect('settings:index')
    
    # Exchange the code for an access token using the predefined redirect URI
    data = {
        'client_id': settings.DISCORD_CLIENT_ID,
        'client_secret': settings.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.DISCORD_REDIRECT_URI,
        'scope': 'identify bot applications.commands',
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Get token
    response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    if response.status_code != 200:
        messages.error(request, "Failed to obtain Discord authorization")
        return redirect('settings:settings')
    
    token_data = response.json()
    access_token = token_data['access_token']
    
    # Get guild (server) information
    guild_headers = {
        'Authorization': f"Bot {settings.DISCORD_BOT_TOKEN}"
    }
    
    # Get guild ID from the URL parameters (the user selected a guild)
    guild_id = request.GET.get('guild_id')
    
    if not guild_id:
        messages.error(request, "No Discord server was selected")
        return redirect('settings:settings')
    
    # Get detailed guild info
    guild_response = requests.get(
        f'https://discord.com/api/v10/guilds/{guild_id}', 
        headers=guild_headers
    )
    
    if guild_response.status_code != 200:
        messages.error(request, "Failed to get Discord server details")
        return redirect('settings:index')
    
    guild_data = guild_response.json()
    
    # Get channel info to select a channel for notifications
    channels_response = requests.get(
        f'https://discord.com/api/v10/guilds/{guild_id}/channels', 
        headers=guild_headers
    )
    
    if channels_response.status_code != 200:
        messages.error(request, "Failed to get Discord channels")
        return redirect('settings:settings')
    
    channels = channels_response.json()
    text_channels = [c for c in channels if c['type'] == 0]  # 0 = text channel
    
    # For simplicity, use the first text channel for notifications
    channel_id = text_channels[0]['id'] if text_channels else None
    channel_name = text_channels[0]['name'] if text_channels else None
    
    if not channel_id:
        messages.error(request, "No valid text channel found in the server")
        return redirect('settings:settings')
    
    # Get server member count
    members_response = requests.get(
        f'https://discord.com/api/v10/guilds/{guild_id}?with_counts=true', 
        headers=guild_headers
    )
    members_data = members_response.json()
    member_count = members_data.get('approximate_member_count', 0)
    
    # Save the Discord connection info
    discord_channel, created = UserNotificationChannel.objects.update_or_create(
        user=request.user, 
        channel='discord',
        defaults={
            'enabled': True,
            'oauth_token': settings.DISCORD_BOT_TOKEN,  # Store bot token, not user token
            'channel_id': channel_id,
            'channel_name': channel_name,
            'workspace_name': guild_data.get('name'),
            'workspace_icon': f"https://cdn.discordapp.com/icons/{guild_id}/{guild_data.get('icon')}.png" if guild_data.get('icon') else None,
            'details': json.dumps({
                'server_id': guild_id,
                'region': guild_data.get('region', 'unknown'),
                'member_count': member_count,
                'bot_name': 'Uptobot Alerts',  # Your bot name
                'permissions': ['Send Messages', 'Read Message History', 'Embed Links']
            })
        }
    )
    
    messages.success(request, "Successfully connected to Discord!")
    return redirect('settings:settings')

