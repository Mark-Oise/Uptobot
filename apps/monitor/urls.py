from django.urls import path
from . import views, utils

app_name = 'monitor'

urlpatterns = [
    path('monitors/', views.monitor_list, name='monitor_list'),
    path('monitors/<slug:slug>/', views.monitor_detail, name='monitor_detail'),
    # path('monitor/<slug:slug>/response-time-chart/', views.response_time_chart, name='response_time_chart'),
    

    # Utilities
    path('delete/<slug:slug>/', utils.delete_monitor, name='delete_monitor'),
    path('search/', utils.search_monitors, name='search_monitors'),
    path('metrics/<slug:slug>/', utils.monitor_metrics, name='monitor_metrics'),

    # HTMX Fragments for metric updates
    path('monitor/<slug:slug>/health_score/', utils.monitor_health_score, name='monitor_health_score'),
    path('monitor/<slug:slug>/uptime-history/', utils.uptime_history, name='uptime_history'),
    path('monitor/<slug:slug>/recent-incidents/', utils.recent_incidents, name='recent_incidents'),
    path('monitor/<slug:slug>/chart/', utils.response_time_chart, name='response_time_chart'),
   
]