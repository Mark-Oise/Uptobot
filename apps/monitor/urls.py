from django.urls import path
from .views import monitor_list, monitor_detail, add_monitor, search_monitors, settings, delete_monitor, response_time_chart

app_name = 'monitor'

urlpatterns = [
    path('monitors/', monitor_list, name='monitor_list'),
    path('monitors/<int:pk>/', monitor_detail, name='monitor_detail'),
    path('add/', add_monitor, name='add_monitor'),
    path('delete/<int:pk>/', delete_monitor, name='delete_monitor'),
    path('search/', search_monitors, name='search_monitors'),
    path('settings/', settings, name='settings'),
    path('monitor/<int:pk>/response-time-chart/', response_time_chart, name='response_time_chart'),
]