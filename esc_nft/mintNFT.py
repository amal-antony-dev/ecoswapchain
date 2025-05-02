import requests
from esc_transaction.serializer import NFTTransactionSerializer
from django.core.exceptions import ValidationError
from requests.exceptions import RequestException
from esc_order.models import SwapOrder
from django.db import transaction
import requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from decimal import Decimal
from .sus_predict import calculate_reward
from esc_wallet.tasks import initiateTransfer

def mint(nft):
    """Mints an NFT and deducts SwapCoin balance securely."""

    # Check if user has sufficient SwapCoin balance
    if nft.owner.wallet.balance < 20:
        raise Exception("❌ Insufficient SwapCoin balance. Minimum 20 required.")

    try:
        metadata = {
            "name": nft.name,
            "symbol": nft.symbol,
            "uri": "https://gateway.pinata.cloud/ipfs/QmYqMyB69WuffQc2rZaLdgXJD1JXDQaxDWo2XM62GPatez",
        }
        
        mintMode = "NFT"
        response = requests.post(
            f"http://localhost:3000/{mintMode}/mint",  # Replace with actual API URL
            json={
                "publicKey": nft.owner.wallet.public_key,
                "metadata": metadata
            }
        )

        # Check response status
        if response.status_code == 200:
            result = response.json()
            txData = result.get("txData")

            if not txData:
                raise Exception("❌ Minting failed: No transaction data returned.")

            # Deduct balance only after a successful transaction
            nft.owner.wallet.balance -= 20
            nft.owner.wallet.save()

            # Update NFT address
            if txData.get("nftType") == "NFT":
                nft.address = txData["mintAddress"]
                nft.nft_type = "NFT"
                nft.status = True
                nft.save()
            
            # Prepare transaction data
            
            print(txData)
            
            data = {
                "transaction_hash": txData["txHash"],
                "transfered_to": nft.owner.wallet.pk,  # Ensure this is the wallet ID, not object
                "asset": nft.pk,  # Ensure this is the NFT ID, not object 
                "status": "CONFIRMED",
            }
            
            # Validate and save the transaction
            tx_serializer = NFTTransactionSerializer(data=data)
            if tx_serializer.is_valid():
                tx = tx_serializer.save()
                return { 
                    "txHash": txData["txHash"],  # Fixed incorrect key from "tsHash"
                    "mintAddress": txData["mintAddress"]
                }       
            else:
                print("❌ Serializer validation failed:", tx_serializer.errors)
                return None

        else:
            print(f"❌ Minting failed: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def transfer_nft_price(order):
    try:
        
        channel_layer = get_channel_layer()
        
        response = requests.get(f'http://localhost:3000/token/reward/{order.seller.wallet.public_key}/{order.escrow_transaction.amount}')
        response.raise_for_status()  

        data = response.json()
        
        order.seller.wallet.balance = order.seller.wallet.balance + Decimal(order.escrow_transaction.amount)
        order.buyer.wallet.balance = order.buyer.wallet.balance - Decimal(order.escrow_transaction.amount)
        order.seller.wallet.save()
        order.buyer.wallet.save()
        
        order.payment_status = "paid"
      
        if order.shipping_details.shipping_method == "self":
            order.status = "completed"
        order.save()
        
        order.escrow_transaction.status = "CONFIRMED"
        order.escrow_transaction.transaction_type = "SELL"
        order.escrow_transaction.transaction_hash = data['tx']
        order.escrow_transaction.save()
        
        initiateTransfer.delay(order.seller.wallet.pk, "REWARD", order.item.reward/2)
        
        
        async_to_sync(channel_layer.group_send)(
            f'order_{order.id}',
            {
                'type' : 'ownership_transfer',
                'transactionHash' : data['tx'],
                'tranactionType' : order.escrow_transaction.transaction_type,
                'status' : order.escrow_transaction.status,
                'payment_status' : order.payment_status,
            }
        )
        
    except RequestException as e:
        raise RequestException(f"Error during request: {e}")
    except ValueError as e:
        raise ValueError(f"Data error: {e}")
    except ValidationError as e:
        raise ValidationError(f"Serialization error: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")


def transfer(orderId, tx_hash):
    """Transfers an NFT to a new address and records the transaction."""
    try:
        
        channel_layer = get_channel_layer()
        
        order = SwapOrder.objects.select_related('item', 'buyer__wallet', 'seller__wallet').get(id=orderId)

        # 2. 🧾 Save all DB updates in a safe atomic block
        with transaction.atomic():
            order.item.owner = order.buyer
            order.item.total_owners = order.item.total_owners + 1
            order.item.in_processing = False
            order.item.active = False
            order.item.save()

            tx_serializer = NFTTransactionSerializer(data={
                "transaction_hash": tx_hash,
                "transfered_to": order.buyer.wallet.pk,
                "transfered_from": order.seller.wallet.pk,
                "asset": order.item.pk,
                "status": "CONFIRMED",
                "transaction_type": "transfer"
            })

            calculate_reward(order.item.id)

            if tx_serializer.is_valid():
                tx_obj = tx_serializer.save()
                order.ownership_transfer_transaction = tx_obj
                order.ownership_transfer_status = "confirmed"
                order.save()
            else:
                print("❌ Serializer errors:", tx_serializer.errors)
                raise Exception("Transaction serialization failed.")

        # 3. 📢 Notify via WebSocket
        async_to_sync(channel_layer.group_send)(
            f'order_{orderId}',
            {
                'type': 'nft_transfer',
                'transactionData': tx_serializer.data,
                'ownershipTransferStatus': order.ownership_transfer_status
            }
        )

        # 4. 💸 Complete escrow + balance update
        transfer_nft_price(order)

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        raise
    except Exception as e:
        print(f"❌ Transfer error: {e}")
        raise
