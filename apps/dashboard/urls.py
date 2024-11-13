# apps/dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard home page
    path('', views.dashboard_home, name='dashboard_home'),  # URL: /dashboard/

    # Profile edit page
    # path('profile/edit/', views.profile_edit, name='profile_edit'),  # URL: /dashboard/profile/edit/

    # Add more views for your dashboard if needed, e.g., settings, notifications, etc.
    # path('settings/', views.settings_view, name='dashboard_settings'),  # Example: /dashboard/settings/
]
