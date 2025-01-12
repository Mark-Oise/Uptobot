from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('notifications/', views.full_notification_list, name='list'),
    path('<int:notification_id>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),

]