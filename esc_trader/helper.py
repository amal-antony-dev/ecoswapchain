import requests
import json
from esc_wallet.serializer import WalletSerializer
from esc_transaction.serializer import TokenTransactionSerializer
import secrets
import string

# Function to generate a secure 8-character encryption key
def generate_secure_encryption_key():
    # Define possible characters (uppercase, lowercase, digits, and special characters)
    characters = string.ascii_letters + string.digits + string.punctuation

    # Generate a random 8-character string
    encryption_key = ''.join(secrets.choice(characters) for _ in range(12))
    
    return encryption_key



def create_wallet():
    try:
        url = "http://localhost:3000/token/transfer/"
        encryption_key = generate_secure_encryption_key()

        headers = {
            "Authorization": f"Bearer {encryption_key}",  # Secure way to send key
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        response_data = response.json()
        
        print(response_data)  # Debugging: Print response to check structure

        wallet_data = response_data.get("wallet", {})
        signature = response_data.get("signature")  # Fix: Correct way to access signature

        data = {
            "public_key": wallet_data.get("publicKey"),  # Use `.get()` to avoid KeyError
            "private_key": wallet_data.get("privateKey"),
            "balance": 100 if signature else 0  # Fix: Use fetched signature
        }

        wallet_serializer = WalletSerializer(data=data, context={"key": encryption_key})
        wallet_serializer.is_valid(raise_exception=True)
        wallet = wallet_serializer.save()
        
        transactionData = {
            "transaction_hash": signature,
            "amount": 100,
            "transfered_to": wallet.id,
            "transaction_type" : "REWARD",
            "status" : "CONFIRMED"
        }
        
        transaction_serializer = TokenTransactionSerializer(data=transactionData)
        transaction_serializer.is_valid(raise_exception=True)
        transaction_serializer.save()
        
        return {
            "wallet": wallet,
            "key": encryption_key
        }
    except Exception as e:
        print(f"Error: {e}")
        return str(e)
