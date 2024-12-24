from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
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
@require_http_methods(['POST'])
def mark_as_read(request, pk):
    """Mark a notification as read and trigger updates"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    response = HttpResponse(status=200)
    response['HX-Trigger'] = 'notification-update'
    return response


@login_required
@require_http_methods(['GET'])
def notification_count(request):
    """Return notification count for HTMX request."""
    return render(request, 'components/notification_count.html', {})


