from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user_group = f"notifications_{self.scope['user'].id}"
            await self.channel_layer.group_add(
                self.user_group,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

    async def notification_message(self, event):
        """Send notification HTML directly"""
        await self.send(text_data=event["notification"])


    

    

    