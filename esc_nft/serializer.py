from rest_framework import serializers
from esc_product.models import Product, ProductImage, MainCategory, RootCategory
from .models import NFT

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["features", "condition", "material"]


class NFTSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFT
        fields = ["id", "name", "symbol", "description", "price", "exchange", "mainImage", "timestamp"]
        
class NFTListSerializer(serializers.ModelSerializer):
    features = serializers.JSONField(source="product.features")  # Flatten features
    condition = serializers.CharField(source="product.condition")  # Flatten condition
    material = serializers.CharField(source="product.material")  # Flatten material

    class Meta:
        model = NFT
        fields = ["id", "name", "description", "mainImage", "uri", "price", "symbol", "nftType", "features", "material", "condition"]

