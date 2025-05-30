from django.urls import path
from . import views, utils

app_name = 'settings'

urlpatterns = [
    path('settings/', views.settings_view, name='settings'),
    path('slack/connect/', views.slack_oauth_connect, name='slack_oauth_connect'),
    path('slack/callback/', views.slack_oauth_callback, name='slack_oauth_callback'),
    path('slack/change-channel/', views.slack_change_channel, name='slack_change_channel'),
    path('slack/disconnect/', views.slack_disconnect, name='slack_disconnect'),
    path('discord/connect/', views.discord_oauth_connect, name='discord_oauth_connect'),
    path('discord/callback/', views.discord_oauth_callback, name='discord_oauth_callback'),
    path('discord/change-channel/', views.discord_change_channel, name='discord_change_channel'),
    path('discord/disconnect/', views.discord_disconnect, name='discord_disconnect'),
    path('toggle-notification/', utils.toggle_notification, name='toggle_notification'),
]
