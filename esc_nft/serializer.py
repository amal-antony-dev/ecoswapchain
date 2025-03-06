from rest_framework import serializers
from esc_product.models import Product, ProductImage, MainCategory, RootCategory
from .models import NFT
from rest_framework import serializers
from esc_product.serializer import ProductSerializer


class NFTSerializer(serializers.ModelSerializer):
    product = ProductSerializer
    class Meta:
        model = NFT
        fields = ["id", "name", "symbol", "description", "price", 'product', "exchange", "mainImage", "timestamp"]
        
        
        
class NFTListSerializer(serializers.ModelSerializer):
    rootCategory= serializers.CharField(source="product.rootCategory.name")  # Flatten features
    mainCategory = serializers.CharField(source="product.mainCategory.name")  # Flatten condition
    features = serializers.JSONField(source="product.features")  # Flatten features
    condition = serializers.CharField(source="product.condition")  # Flatten condition
    image = serializers.ImageField(source="mainImage")  # Rename mainImage to image

    class Meta:
        model = NFT
        fields = ["id", "address", "name", "description", "image", "uri", "price", "symbol", "nftType", "features", "rootCategory", "mainCategory", "condition"]


class NFTDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    image = serializers.ImageField(source="mainImage")  # Rename mainImage to image
    ownerPublicKey = serializers.CharField(source="owner.wallet.public_key")  # Flatten owner's public key
    createdAt = serializers.DateTimeField(source="timestamp")  # Rename timestamp to createdAt
    leafIndex = serializers.IntegerField(source="leaf_index")  # Rename leaf_index to leafIndex
    treeAddress = serializers.CharField(source="tree_address")  # Rename tree_address to treeAddress
    class Meta:
        model = NFT
        fields = ["id", "address", "name", "description", "price", "product",
                  "exchange", "image", "timestamp", "nftType", "leafIndex", 
                  "treeAddress", "uri", "ownerPublicKey", "createdAt", 'status']