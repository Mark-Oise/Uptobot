from django.urls import path
from . import views
from . import webhooks

app_name = 'subscriptions'

urlpatterns = [
    path('subscription/', views.subscription, name='subscription'),
    path('checkout/<str:plan_type>/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.subscription_success, name='subscription_success'),
    path('webhook/polar/', webhooks.handle_polar_webhook, name='polar_webhook'),
]