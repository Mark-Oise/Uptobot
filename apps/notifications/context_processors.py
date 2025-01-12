from .models import Notification

def notifications(request):
    """Context processor to add notifications and count to template context."""
    if request.user.is_authenticated:
        notifications_queryset = (Notification.objects
                                .filter(user=request.user, is_read=False)
                                .select_related('monitor')
                                .order_by('-created_at'))
        
        notification_count = notifications_queryset.count()
        # Only get the first 5 for display in dropdown
        notifications = notifications_queryset[:5]
        
        return {
            'notifications': notifications,
            'notification_count': notification_count,
            'has_more_notifications': notification_count > 5
        }
    return {
        'notifications': [],
        'notification_count': 0,
        'has_more_notifications': False
    }




