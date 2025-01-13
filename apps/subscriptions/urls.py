from django.urls import path
from .views import subscription

app_name = 'subscriptions'

urlpatterns = [
    path('subscription/', subscription, name='subscription'),
]