from rest_framework import serializers
from .models import SwapOrder, Message

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.IntegerField(source="sender.id")
    
    class Meta:
        model = Message
        fields = "__all__"
        

class OrderListSerializer(serializers.ModelSerializer):
    ownerId = serializers.IntegerField(source="item.owner.eco_user.id") 
    buyerAddress = serializers.CharField(source="buyer.wallet.public_key")
    sellerAddress = serializers.CharField(source="seller.wallet.public_key")
    nftName = serializers.CharField(source="item.name")
    nftImageUrl = serializers.CharField(source="item.mainImage.url")
    nftSymbol = serializers.CharField(source="item.symbol")
    createdAt = serializers.DateTimeField(source="created_at")
    orderType = serializers.SerializerMethodField()
    class Meta:
        model = SwapOrder
        fields = ["id", "ownerId", "buyerAddress", "sellerAddress", "nftName", "nftImageUrl", "nftSymbol", "status", "createdAt", "orderType"]
        
    def get_orderType(self, obj):
        return None
        
       

class OrderSerializer(serializers.ModelSerializer):
    orderId = serializers.UUIDField(source="id")
    buyerName = serializers.CharField(source="buyer.eco_user.username")
    sellerName = serializers.CharField(source="seller.eco_user.username")
    buyerAddress = serializers.CharField(source="buyer.wallet.public_key")
    sellerAddress = serializers.CharField(source="seller.wallet.public_key")
    nftName = serializers.CharField(source="item.name")
    nftImageUrl = serializers.CharField(source="item.mainImage.url")
    nftSymbol = serializers.CharField(source="item.symbol")
    nftAddress = serializers.CharField(source="item.address")
    nftUri = serializers.CharField(source="item.uri")
    orderStatus = serializers.CharField(source="status")
    paymentStatus = serializers.CharField(source="payment_status")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = SwapOrder
        fields = "__all__"