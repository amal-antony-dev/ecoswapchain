import requests
from esc_transaction.serializer import NFTMintTransactionSerializer

def mint(nft):
    """Mints an NFT and deducts SwapCoin balance securely."""

    # Check if user has sufficient SwapCoin balance
    if nft.owner.wallet.balance < 20:
        raise Exception("❌ Insufficient SwapCoin balance. Minimum 20 required.")

    # Construct metadata correctly


    try:
        metadata = {
        "name": nft.name,
        "symbol": nft.symbol,
        "uri" : "https://gateway.pinata.cloud/ipfs/QmYqMyB69WuffQc2rZaLdgXJD1JXDQaxDWo2XM62GPatez",
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
            print(f"✅ NFT Minted! Transaction ID: {result.get('transactionId')}")

            # Deduct balance only after a successful transaction
            nft.owner.wallet.balance -= 20
            nft.owner.wallet.save()
            return result
        
        
        else:
            print(f"❌ Minting failed: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
