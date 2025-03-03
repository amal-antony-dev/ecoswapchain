from rest_framework import serializers
from esc_wallet.models import Wallet
from esc_transaction.serializer import TokenTransactionSerializer

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['public_key', 'private_key', 'key']
        
    def create(self, validated_data):

        wallet = Wallet.objects.create(**validated_data)
        wallet.set_key(validated_data["key"])
        wallet.save()
        return wallet

class WalletRetrieveSerializer(serializers.ModelSerializer):
    sent_transaction = TokenTransactionSerializer(source="sent_token_transactions", many=True)
    recieved_transaction = TokenTransactionSerializer(source="received_token_transactions", many=True)
    class Meta:
        model = Wallet
        fields = ['public_key', 'balance', 'sent_transaction', 'recieved_transaction']
        