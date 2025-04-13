import requests
from requests.exceptions import RequestException
from rest_framework.exceptions import ValidationError
from esc_transaction.serializer import TokenTransactionCreationSerializer, TokenTransactionSerializer
from decimal import Decimal
from .models import Wallet
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

def transferFromTreasury(walletPk, transaction_type, amount=0,):
    try:
        wallet = Wallet.objects.get(id=walletPk)
        response = requests.get(f'http://localhost:3000/token/reward/{wallet.public_key}/{amount}')
        response.raise_for_status()  # Raise an error for non-200 responses
        data = response.json()
        wallet.balance = wallet.balance + Decimal(amount)
        wallet.save()
        transactionData = {
            "transaction_hash": data['tx'],
            "amount": amount,
            "transfered_to": walletPk,
            "transaction_type": transaction_type,
            "status": "CONFIRMED"
        }
        transaction_serializer = TokenTransactionCreationSerializer(data=transactionData)
        if transaction_serializer.is_valid():
            transaction = transaction_serializer.save()
            async_to_sync(channel_layer.group_send)(
                f'wallet_{wallet.public_key}',
                {
                    'type': 'transactionComplete',
                    'transactionData': transaction_serializer.data
                }
            )
        else:
            raise ValidationError(transaction_serializer.errors)

    except RequestException as e:
        raise RequestException(f"Request error: {e}")
    except ValueError as e:
        raise ValueError(f"Value error: {e}")
    except ValidationError as e:
        raise ValidationError(f"Validation error: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")
