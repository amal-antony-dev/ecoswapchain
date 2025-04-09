from django.dispatch import Signal, receiver
from requests.exceptions import RequestException
from rest_framework.exceptions import ValidationError
from decimal import Decimal
import requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

nft_transfer_signal = Signal()

@receiver(nft_transfer_signal)
def transfer_nft_price(sender, order, **kwargs):
    try:
        response = requests.get(f'http://localhost:3000/token/reward/{order.seller.wallet.public_key}/{order.escrow_transaction.amount}')
        response.raise_for_status()  

        data = response.json()
        
        order.seller.wallet.balance = order.seller.wallet.balance + Decimal(order.escrow_transaction.amount)
        order.seller.wallet.save()
        
        order.item.owner = order.buyer
        order.item.in_processing = False
        order.item.save()
        
        order.payment_status = "paid"
        order.save()
        
        order.escrow_transaction.status = "CONFIRMED"
        order.escrow_transaction.transaction_hash = data['tx']
        order.escrow_transaction.save()
        
        async_to_sync(channel_layer.group_send)(
            f'order_{order.id}',
            {
                'type' : 'ownership_transfer',
                'transactionHash' : data['tx'],
                'timestamp' : order.escrow_transaction.time_stamp,
                'status' : order.escrow_transaction.status,
                'payment_status' : order.payment_status,
            }
        )
        
    except RequestException as e:
        print(f"Error during request: {e}")
    except ValueError as e:
        print(f"Data error: {e}")
    except ValidationError as e:
        print(f"Serialization error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")