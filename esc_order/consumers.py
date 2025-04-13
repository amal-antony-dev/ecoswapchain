from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Message, SwapOrder
from esc_user.models import EcoUser
from .serializer import MessageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'chat_{self.order_id}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']
        
        

        print(f"📩 Received message from {sender}: {message}")  # Debug log

        # Save the message to the database
        messageObject = await self.save_message(sender, message)
        message_data = MessageSerializer(messageObject).data

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_data["message"],
                'sender': message_data["sender"],
                'timestamp': message_data["timestamp"],
        }
    )


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
        }))

    @database_sync_to_async
    def save_message(self, sender_user_id, message):
        order = SwapOrder.objects.get(id=self.order_id)
        sender = EcoUser.objects.get(id=sender_user_id)
        message = Message.objects.create(order=order, sender=sender, message=message)
        return message
    

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.order_id}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    async def order_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'shippingMethod': event['shippingMethod'],
            'sourceHub': event['sourceHub'],
            'destinationHub': event['destinationHub'],
        }))
        
    async def update_price(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'update_price',
            'updated_price' : event['updated_price']
        }))
        
    async def buyer_confirmation(self, event):
        await self.send(text_data=json.dumps({
            'type' : "buyer_confirmation",
        }))
        
    async def seller_confirmation(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'seller_confirmation',
        }))
    
    async def ownership_transfer(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'ownership_transfer',
            'transactionHash' : event['transactionHash'],
            'timestamp' : event['timestamp'],
            'status' : event['status'],
            'payment_status' : event['payment_status'],
        }))
        
    async def nft_transfer(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'nft_transfer',
            'transactionData' : event['transactionData'],
            'ownershipTransferStatus' : event['ownershipTransferStatus']
        }))
    
    async def initiate_escrow(self, event):
        await self.send(text_data = json.dumps({
            'type' : 'initiate_escrow',
            'transactinData' : event['transactionData']
        })) 