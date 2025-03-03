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