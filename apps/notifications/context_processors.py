from .models import Notification

def notifications(request):
    """Context processor to add notifications to template context."""
    if request.user.is_authenticated:
        notifications = (Notification.objects
                        .filter(user=request.user, is_read=False)
                        .select_related('monitor')
                        .order_by('-created_at')[:5])
        return {'notifications': notifications}
    return {'notifications': []}



def notification_count(request):
    """Context processor to add notification count to template context."""
    if request.user.is_authenticated:
        notification_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'notification_count': notification_count}
    return {'notification_count': 0}