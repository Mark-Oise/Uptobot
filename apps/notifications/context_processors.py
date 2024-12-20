from .models import Notification

def notifications(request):
    """Context processor to add notifications to template context."""
    if request.user.is_authenticated:
        notifications = (Notification.objects
                        .filter(user=request.user)
                        .select_related('monitor')
                        .order_by('-created_at')[:5])
        return {'notifications': notifications}
    return {'notifications': []}


def notification_count(request):
    """Context processor to add unread notification count"""
    if request.user.is_authenticated:
        count = Notification.get_unread_count(request.user)
        return {'unread_notification_count': count}
    return {'unread_notification_count': 0}