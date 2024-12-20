from django.urls import path
from . import views

app_name = 'monitor'

urlpatterns = [
    path('monitors/', views.monitor_list, name='monitor_list'),
    path('monitors/<slug:slug>/', views.monitor_detail, name='monitor_detail'),
    path('add/', views.add_monitor, name='add_monitor'),
    path('delete/<slug:slug>/', views.delete_monitor, name='delete_monitor'),
    path('search/', views.search_monitors, name='search_monitors'),
    path('settings/', views.settings, name='settings'),
    path('monitor/<slug:slug>/response-time-chart/', views.response_time_chart, name='response_time_chart'),
]