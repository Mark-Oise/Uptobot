from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
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
                    .filter(user=request.user)
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
        while True:
            # Get new notifications
            notifications = (Notification.objects
                           .filter(user=request.user, is_read=False)
                           .select_related('monitor')
                           .order_by('-created_at')[:5])
            
            if notifications.exists():
                # Render notification HTML
                html = render_to_string(
                    'components/notifications/notification_items.html',
                    {'notifications': notifications},
                    request=request
                )
                
                # Create SSE data
                data = {
                    'html': html,
                    'count': notifications.count()
                }
                
                yield f"data: {json.dumps(data)}\n\n"
            
            time.sleep(3)  # Poll every 3 seconds

    response = HttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response

@login_required
@require_http_methods(['POST'])
def mark_as_read(request, pk):
    """Mark a single notification as read"""
    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user
    )
    notification.mark_as_read()
    
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    return HttpResponse(status=204)

@login_required
@require_http_methods(['POST'])
def mark_all_as_read(request):
    """Mark all notifications as read"""
    Notification.mark_all_as_read(request.user)
    
    if request.headers.get('HX-Request'):
        # Return empty notification list for HTMX to update the UI
        context = {'notifications': []}
        return render(request, 'notifications/components/notification_items.html', context)
    
    return HttpResponse(status=204)

@login_required
@require_http_methods(['GET'])
def notification_count(request):
    """Get unread notification count for the badge"""
    count = Notification.get_unread_count(request.user)
    
    if request.headers.get('HX-Request'):
        return HttpResponse(
            f'<span class="notification-count">{count}</span>',
            content_type='text/html'
        )
    
    return HttpResponse(
        json.dumps({'count': count}),
        content_type='application/json'
    )
