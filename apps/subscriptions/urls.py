from django.urls import path
from .views import subscription, create_checkout_session, subscription_success

app_name = 'subscriptions'

urlpatterns = [
    path('subscription/', subscription, name='subscription'),
    path('create-checkout-session/<str:plan_type>/', create_checkout_session, name='create_checkout_session'),
    path('subscription/success/', subscription_success, name='subscription_success'),
]