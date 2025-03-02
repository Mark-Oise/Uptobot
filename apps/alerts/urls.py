from django.urls import path
from .views import email_incident

urlpatterns = [
    path('email/', email_incident, name='email_incident'),
]