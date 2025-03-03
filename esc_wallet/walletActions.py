import requests
from requests.exceptions import RequestException
from rest_framework.exceptions import ValidationError
from .models import Wallet
from esc_transaction.serializer import TokenTransactionCreationSerializer

def transferFromTreasury(wallet, amount=0):
    try:
        response = requests.get(f'http://localhost:3000/token/reward/{wallet.public_key}/{amount}')
        response.raise_for_status()  # Raise an error for non-200 responses

        data = response.json()
        
        transactionData = {
            "transaction_hash": data['tx'],
            "amount": amount,
            "transfered_to": wallet.pk,
            "transaction_type": "REWARD",
            "status": "CONFIRMED"
        }

        transaction_serializer = TokenTransactionCreationSerializer(data=transactionData)
        if transaction_serializer.is_valid():
            transaction_serializer.save()
            return transaction_serializer.data
        else:
            raise ValidationError(transaction_serializer.errors)

    except RequestException as e:
        print(f"Error during request: {e}")
    except ValueError as e:
        print(f"Data error: {e}")
    except ValidationError as e:
        print(f"Serialization error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
