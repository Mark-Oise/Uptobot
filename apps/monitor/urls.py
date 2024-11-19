from django.urls import path
from .views import monitor_list, monitor_detail, add_monitor, protocol_fields

app_name = 'monitor'

urlpatterns = [
    path('', monitor_list, name='monitor_list'),
    path('<int:pk>/', monitor_detail, name='monitor_detail'),
    path('add/', add_monitor, name='add_monitor'),
    path('protocol_fields/', protocol_fields, name='protocol_fields'),
]