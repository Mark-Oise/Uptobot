from .models import Notification

def notifications(request):
    """Context processor to add notifications and count to template context."""
    if request.user.is_authenticated:
        notifications = (Notification.objects
                        .filter(user=request.user, is_read=False)
                        .select_related('monitor')
                        .order_by('-created_at'))
        notification_count = notifications.count()
        return {
            'notifications': notifications,
            'notification_count': notification_count
        }
    return {
        'notifications': [],
        'notification_count': 0
    }




