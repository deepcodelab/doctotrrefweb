# backend/video/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = self.scope['url_route']['kwargs']['room']
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room, self.channel_name)

    async def receive(self, text_data):
        """
        Expect JSON messages with keys like:
        { "type": "offer", "sdp": {...} }
        { "type": "answer", "sdp": {...} }
        { "type": "candidate", "candidate": {...} }
        """
        data = json.loads(text_data)
        # Re-broadcast to the group (except you — handled by clients)
        await self.channel_layer.group_send(
            self.room,
            {
                "type": "signal.message",
                "message": data,
                "sender_channel": self.channel_name,
            }
        )

    async def signal_message(self, event):
        # Forward message to WebSocket clients
        # Optionally filter out the original sender by checking channel_name in client side
        await self.send(text_data=json.dumps(event["message"]))
