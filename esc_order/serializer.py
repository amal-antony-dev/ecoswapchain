from rest_framework import serializers
from .models import SwapOrder, Message, Address, ShippingDetails
from esc_hub.serializers import HubRetrieveSerializer, RouteSerializer
from esc_transaction.serializer import TokenTransactionSerializer, NFTTransactionRetrieveSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.IntegerField(source="sender.id")
    
    class Meta:
        model = Message
        fields = "__all__"
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        
        
class ShippingDetailsSerializer(serializers.ModelSerializer):
    buyer_address = AddressSerializer()
    seller_address = AddressSerializer()
    isSellerConfirmed = serializers.BooleanField(source="shipping_confirmed_by_seller")
    isBuyerConfirmed = serializers.BooleanField(source="shipping_confirmed_by_buyer")
    shippingMethod = serializers.CharField(source="shipping_method")
    trackingNumber = serializers.CharField(source="tracking_number")
    sourceHub = HubRetrieveSerializer(source="source_hub")
    destinationHub = HubRetrieveSerializer(source="destination_hub")
    shippingRoutes = RouteSerializer(source="shipping_route", many=True)
    verificationStatus = serializers.CharField(source='product_verified')
    class Meta:
        model = ShippingDetails
        fields = ["buyer_address", "seller_address", "isSellerConfirmed",
                  "isBuyerConfirmed", "shippingMethod", "trackingNumber",
                  "sourceHub", "destinationHub", "shippingRoutes", "verificationStatus"]

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
    ownerId = serializers.IntegerField(source="seller.eco_user.id")
    nftName = serializers.CharField(source="item.name")
    nftImageUrl = serializers.CharField(source="item.mainImage.url")
    nftSymbol = serializers.CharField(source="item.symbol")
    nftAddress = serializers.CharField(source="item.address")
    nftUri = serializers.CharField(source="item.uri")
    orderStatus = serializers.CharField(source="status")
    paymentStatus = serializers.CharField(source="payment_status")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")
    shippingDetails = ShippingDetailsSerializer(source="shipping_details")
    escrowTransaction = TokenTransactionSerializer(source="escrow_transaction")
    ownershipTransferTransaction = NFTTransactionRetrieveSerializer(source="ownership_transfer_transaction")
    ownershipTransferStatus = serializers.CharField(source="ownership_transfer_status")
   
    class Meta:
        model = SwapOrder
        fields = [
            "orderId",
            "buyerName",
            "sellerName",
            "buyerAddress",
            "sellerAddress",
            "ownerId",
            "nftName",
            "nftImageUrl",
            "nftSymbol",
            "nftAddress",
            "nftUri",
            "orderStatus",
            "paymentStatus",
            "createdAt",
            "updatedAt",
            "price",
            "shippingDetails",
            "escrowTransaction",
            "ownershipTransferTransaction",
            'ownershipTransferStatus',
   
        ]



class OrderHubSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='pk', read_only=True)
    sellerName = serializers.CharField(source='seller.eco_user.username', read_only=True)
    buyerName = serializers.CharField(source='buyer.eco_user.username', read_only=True)
    productName = serializers.CharField(source='item.name', read_only=True)
    shippingMethod = serializers.CharField(source='shipping_details.shipping_method', read_only=True)
    verificationStatus = serializers.CharField(source='shipping_details.product_verified', read_only=True)
    address = AddressSerializer(source='shipping_details.seller_address', read_only=True)
    orderDate = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = SwapOrder
        fields = ["id", "sellerName", "buyerName", "productName", "shippingMethod", "verificationStatus", "address", "orderDate", "price"]