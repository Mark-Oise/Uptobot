import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return


        self.notification_group = f'notifications_{self.user.public_id}'

        await self.channel_layer.group_add(
            self.notification_group, 
            self.channel_name)
        
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'notification_group'):
            await self.channel_layer.group_discard(
                self.notification_group,
            self.channel_name
        )
    
    async def notification_message(self, event):
        """Handle incoming notification messages"""
        notification = event["notification"]
        html = await self.render_notification(notification)
        count = await self.get_unread_notification_count()
        
        # Create the message with OOB swap directives
        message = f"""
            <div id="notification-list" hx-swap-oob="afterbegin">{html}</div>
            <div id="notification-count" hx-swap-oob="innerHTML">{count}</div>
        """
        
        # Send the raw HTML directly
        await self.send(text_data=message)


    @database_sync_to_async
    def get_unread_notification_count(self):
        """Get the current unread notification count for the user"""
        return Notification.objects.filter(
            user=self.user, 
            is_read=False
        ).count()

    @database_sync_to_async
    def render_notification(self, notification):
        """Render the notification HTML template"""
        return render_to_string(
            'components/notifications/notification_items.html',
            {'notification': notification}
        )


    

    

    