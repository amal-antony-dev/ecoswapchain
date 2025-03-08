from rest_framework import serializers
from .models import SwapOrder

class OrderSerializer(serializers.ModelSerializer):
    buyer = serializers.CharField(source="buyer.username")
    seller = serializers.SerializerMethodField(source="seller.username")
    buyerAddress = serializers.CharField(source="buyer.wallet.public_key")
    sellerAddress = serializers.CharField(source="seller.wallet.public_key")
    nftName = serializers.CharField(source="item.name")
    nftImage = serializers.CharField(source="item.image")
    nftSymbol = serializers.CharField(source="item.symbol")
    nftAddress = serializers.CharField(source="item.address")
    nftUri = serializers.CharField(source="item.uri")
    
    class Meta:
        model = SwapOrder
        fields = "__all__"
        

