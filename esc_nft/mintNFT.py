import requests
from esc_transaction.serializer import NFTMintTransactionSerializer
from django.core.exceptions import ValidationError
import requests

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
                nft.save()
            
            # Prepare transaction data
            
            print(txData)
            
            data = {
                "transaction_hash": txData["txHash"],
                "minted_to": nft.owner.wallet.pk,  # Ensure this is the wallet ID, not object
                "asset": nft.pk,  # Ensure this is the NFT ID, not object
                "transaction_type": "MINT",
                "mint_cost": 20.00,  
                "mint_status": "CONFIRMED",
            }
            
            # Validate and save the transaction
            tx_serializer = NFTMintTransactionSerializer(data=data)
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
