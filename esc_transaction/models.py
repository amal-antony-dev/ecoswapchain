from django.db import models

# Create your models here.
class TokenTransaction(models.Model):
    transaction_hash = models.CharField(max_length=200, unique=True, db_index=True)
    time_stamp = models.DateTimeField(auto_now_add=True, db_index=True)
    amount = models.BigIntegerField()
    
    transfered_to = models.ForeignKey(
        "esc_wallet.Wallet", 
        verbose_name=("Receiver"), 
        on_delete=models.CASCADE, 
        related_name="received_token_transactions",
        null=True
    )
    transfered_from = models.ForeignKey(
        "esc_wallet.Wallet", 
        verbose_name=("Sender"), 
        on_delete=models.CASCADE, 
        related_name="sent_token_transactions",
        null=True
    )

    TRANSACTION_TYPES = [
        ("BUY", "Buy"),
        ("ESCROW", "Escrow"),
        ("REWARD", "Reward"),
        ("FEE", "Fee")
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default="REWARD")

    status = models.CharField(max_length=20, choices=[("PENDING", "Pending"), ("HOLD", "Hold"), ("CONFIRMED", "Confirmed"), ("FAILED", "Failed")], default="PENDING")

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.transaction_hash[:10]}"

class NFTMintTransaction(models.Model):
    transaction_hash = models.CharField(max_length=200, unique=True, db_index=True)
    time_stamp = models.DateTimeField(auto_now_add=True, db_index=True)

    minted_to = models.ForeignKey(
        "esc_wallet.Wallet", 
        verbose_name=("Minted To"), 
        on_delete=models.CASCADE, 
        related_name="minted_nfts"
    )
    
    asset = models.OneToOneField(
        "esc_nft.NFT", 
        verbose_name=("NFT"), 
        on_delete=models.CASCADE, 
        related_name="mint_lifecycle", 
        null=True, blank=True
    )
    
    transaction_type = models.CharField(max_length=20, default="MINT")


    mint_cost = models.DecimalField(max_digits=10, decimal_places=5, default=0.0)  # Minting cost
    mint_status = models.CharField(max_length=20, choices=[("PENDING", "Pending"), ("CONFIRMED", "Confirmed"), ("FAILED", "Failed")], default="PENDING")

    def __str__(self):
        return f"NFT minted to {self.minted_to} - {self.transaction_hash[:10]}"


class NFTTransaction(models.Model):
    
    TRANSACTION_TYPES = [
        ("mint", "MINT"),
        ("transfer", "Transfer"),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default="MINT")
    transaction_hash = models.CharField(max_length=200, unique=True, db_index=True)
    time_stamp = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=20, choices=[("PENDING", "Pending"), ("CONFIRMED", "Confirmed"), ("FAILED", "Failed")], default="PENDING")

    transfered_to = models.ForeignKey(
        "esc_wallet.Wallet", 
        verbose_name=("Receiver"), 
        on_delete=models.CASCADE, 
        related_name="received_nfts",
        null=True
    )
    transfered_from = models.ForeignKey(
        "esc_wallet.Wallet", 
        verbose_name=("Sender"), 
        on_delete=models.CASCADE, 
        related_name="sent_nfts",
        null = True
    )
    
    asset = models.ForeignKey(
        "esc_nft.NFT", 
        verbose_name=("NFT"), 
        on_delete=models.CASCADE, 
        related_name="ownership_history", 
        null=True, blank=True
    )


