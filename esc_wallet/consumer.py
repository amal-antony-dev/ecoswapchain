import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WalletConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.public_key = self.scope["url_route"]["kwargs"]["public_key"]
        self.room_group_name = f'wallet_{self.public_key}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to wallet channel {self.public_key}'
        }))
        
    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    # Custom event method
    async def transactionComplete(self, event):   
        await self.send(text_data=json.dumps({
            'type': 'transaction',
            'transactionData': event['transactionData']
        }))
