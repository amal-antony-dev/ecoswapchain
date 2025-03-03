from rest_framework import serializers
from .models import TokenTransaction, NFTMintTransaction, NFTTransferTransaction
from esc_wallet.models import Wallet
from esc_nft.models import NFT
# ✅ Token Transaction Serializer
class TokenTransactionSerializer(serializers.ModelSerializer):
    transfered_to = serializers.SlugRelatedField(slug_field="public_key", queryset=Wallet.objects.all(), allow_null=True)
    transfered_from = serializers.SlugRelatedField(slug_field="public_key", queryset=Wallet.objects.all(), allow_null=True)

    class Meta:
        model = TokenTransaction
        fields = "__all__"
        
class TokenTransactionCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenTransaction
        fields = "__all__"
        
        
        

# ✅ NFT Mint Transaction Serializer
class NFTMintTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFTMintTransaction
        fields = "__all__"


class NFTMintTransactionRetrieveSerializer(serializers.ModelSerializer):
    # Custom fields to return wallet public key and NFT mint address
    wallet_public_key = serializers.CharField(source="minted_to.public_key", read_only=True)
    nft_mint_address = serializers.CharField(source="asset.mint_address", read_only=True)

    class Meta:
        model = NFTMintTransaction
        fields = [
            "transaction_hash",
            "time_stamp",
            "wallet_public_key",
            "nft_mint_address",
            "transaction_type",
            "mint_cost",
            "mint_status"
        ]

    def to_representation(self, instance):
        """Removes null fields from the response for a cleaner API output"""
        data = super().to_representation(instance)
        return {key: value for key, value in data.items() if value is not None}

        
        

# ✅ NFT Transfer Transaction Serializer
class NFTTransferTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFTTransferTransaction
        fields = "__all__"
