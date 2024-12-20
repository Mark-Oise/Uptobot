from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
import json
import time

from .models import Notification


@login_required
def notification_list(request):
    notifications = (Notification.objects
                    .filter(user=request.user)
                    .select_related('monitor')
                    .order_by('-created_at')[:5])
    
    context = {
        'notifications': notifications,
    }

    return render(request, 'components/notification_list.html', context)



@login_required
@require_http_methods(['GET'])
def notification_stream(request):

    def event_stream():
        while True:
            # Get new notifications
            notifications = (Notification.objects.filter(user=request.user)
                             .select_related('monitor')
                             .order_by('-created_at')[:5])
            
            if notifications.exists():
                # Render notification HTML
                html = render_to_string(
                    'components/notifications/notification_items.html',
                    {'notifications': notifications},
                    request=request,
                )
                
                # Create SSE data
                data = {
                    'html': html,
                    'count': notifications.count(),
                }
                
                yield f"data: {json.dumps(data)}\n\n"
                
            time.sleep(3) # Poll every 3 seconds

    response = StreamingHttpResponse(
        event_stream(),
        content_type = 'text/event-stream',
    )
    
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    
    return response



# @login_required
# @require_http_methods(['GET'])
# def notification_count(request):
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
