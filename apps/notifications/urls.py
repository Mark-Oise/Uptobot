from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('stream/', views.notification_stream, name='stream'),
    path('count/', views.notification_count, name='count'),
    path('<int:pk>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
]