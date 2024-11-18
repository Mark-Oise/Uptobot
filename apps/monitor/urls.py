from django.urls import path
from .views import monitor_list, monitor_detail

urlpatterns = [
    path('', monitor_list, name='monitor_list'),
    path('<int:pk>/', monitor_detail, name='monitor_detail'),
]