from rest_framework import serializers
from .models import TokenTransaction, NFTMintTransaction, NFTTransferTransaction
from esc_wallet.models import Wallet

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

# ✅ NFT Transfer Transaction Serializer
class NFTTransferTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFTTransferTransaction
        fields = "__all__"
