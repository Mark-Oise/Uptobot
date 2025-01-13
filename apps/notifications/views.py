from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import json
from django.core.paginator import Paginator
from .models import Notification
from django.shortcuts import redirect



@login_required
def full_notification_list(request):
    """View for the full notifications page"""
    notifications = (Notification.objects
                    .filter(user=request.user, is_read=False)
                    .select_related('monitor')
                    .order_by('-created_at'))
    
    # Paginate notifications
    
    paginator = Paginator(notifications, 6)  # Show 10 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notifications/list.html', {
        'notifications': page_obj
    })


def mark_as_read(request, notification_id):
    """View for marking a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    # If request is from the list page (has HX-Target header), don't redirect to the notification's URL
    if request.headers.get('HX-Target'):
        return redirect('notifications:list')
    
    # Otherwise, redirect to the notification's URL
    response = HttpResponse()
    response['HX-Redirect'] = notification.get_absolute_url()
    return response


def mark_all_as_read(request):
    """View for marking all notifications as read"""
    Notification.mark_all_as_read(request.user)
    return redirect('notifications:list')