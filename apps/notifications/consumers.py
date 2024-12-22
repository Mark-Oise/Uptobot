import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string


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
        
        # Send the rendered notification HTML to the client
        await self.send(text_data=json.dumps({
            "type": "notification",
            "html": html
        }))

    @database_sync_to_async
    def render_notification(self, notification):
        """Render the notification HTML template"""
        return render_to_string(
            'components/notifications/notification_items.html',
            {'notification': notification}
        )


    

    

    