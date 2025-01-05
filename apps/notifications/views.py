from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import json

from .models import Notification

@login_required
def notification_list(request):
    """HTMX endpoint to fetch notifications dropdown content"""
    notifications = (Notification.objects
                    .filter(user=request.user, is_read=False)
                    .select_related('monitor')
                    .order_by('-created_at')[:5])
    
    context = {
        'notifications': notifications,
        'notification_count': notifications.count(),
    }
    
    return render(request, 'components/notification_list.html', context)





# @login_required
# def mark_as_read(request, pk):
#     """Mark notification as read and return updated count"""
#     notification = get_object_or_404(Notification, pk=pk, user=request.user)
#     notification.mark_as_read()
    
#     # Get new count for the badge
#     unread_count = Notification.get_unread_count(request.user)
    
#     response = HttpResponse(status=200)
#     response['HX-Trigger'] = json.dumps({
#         'updateNotificationCount': unread_count
#     })
#     return response





# @login_required
# def notification_count(request):
#     """Return the current number of unread notifications"""
#     unread_count = Notification.get_unread_count(request.user)
#     return HttpResponse(unread_count if unread_count > 0 else '')


