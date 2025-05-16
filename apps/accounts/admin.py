from django.contrib import admin
from .models import User, UserNotificationChannel


admin.site.register(User)
admin.site.register(UserNotificationChannel)
