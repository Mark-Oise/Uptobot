from django.contrib import admin
from .models import Notification
# Register your models here.

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'created_at']
    list_filter = ['severity', 'created_at']
    search_fields = ['title', 'description']
