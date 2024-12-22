from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
import json
import time

from .models import Notification

@login_required
def notification_list(request):
    """Main view for displaying notifications"""
    notifications = (Notification.objects
                    .filter(user=request.user, is_read=False)
                    .select_related('monitor')
                    .order_by('-created_at')[:5])
    
    context = {
        'notifications': notifications,
    }
    
    # If it's an HTMX request, return only the notification items
    if request.headers.get('HX-Request'):
        return render(request, 'components/notifications/notification_items.html', context)
    
    return render(request, 'notifications/notification_list.html', context)


@login_required
@require_http_methods(['GET'])
def notification_stream(request):
    """SSE endpoint for real-time notifications"""
    def event_stream():
        last_notification_id = None
        while True:
            # Get latest notifications
            notifications = Notification.objects.filter(
                user=request.user,
            ).order_by('-created_at')

            if last_notification_id is not None:
                notifications = notifications.filter(id__gt=last_notification_id)

            if notifications.exists():
                last_notification_id = notifications.first().id

            # Render notification HTML
            html = render_to_string(
                'components/notifications/notification_items.html',
                {'notifications': notifications},
                request=request
            )
            
            # Send the HTML directly
            yield f"data: {html}\n\n"
            
            time.sleep(15)  # Poll every 15 seconds

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@login_required
@require_http_methods(['POST'])
def mark_as_read(request, pk):
    """Mark a notification as read and trigger updates"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    response = HttpResponse(status=200)
    response['HX-Trigger'] = 'notification-update'
    return response


@login_required
@require_http_methods(['POST'])
def mark_all_as_read(request):
    """Mark all notifications as read and trigger updates"""
    Notification.mark_all_as_read(request.user)
    
    # Return updated notification list
    notifications = (Notification.objects
                    .filter(user=request.user)
                    .select_related('monitor')
                    .order_by('-created_at')[:5])
    
    response = render(request, 
                     'components/notifications/notification_items.html',
                     {'notifications': notifications})
    response['HX-Trigger'] = 'notification-update'
    return response


@login_required
@require_http_methods(['GET'])
def notification_count(request):
    """Get unread notification count for the badge"""
    count = Notification.get_unread_count(request.user)
    return HttpResponse(count)
