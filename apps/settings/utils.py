from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.accounts.models import UserNotificationChannel
from django.contrib import messages


@login_required
def toggle_notification(request):
    channel = request.POST.get('channel')
    enabled = request.POST.get(f'{channel}_notifications_enabled') == 'on'
    
    if channel in ['email', 'slack', 'discord']:
        notification_channel, created = UserNotificationChannel.objects.get_or_create(
            user=request.user,
            channel=channel,
            defaults={'enabled': enabled}
        )
        if not created:
            notification_channel.enabled = enabled
            notification_channel.save()
            
        messages.success(request, f'{channel.title()} notifications updated successfully.')
        return HttpResponse(status=200)
    
    return HttpResponse(status=400)