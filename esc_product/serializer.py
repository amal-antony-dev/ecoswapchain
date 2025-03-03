from rest_framework import serializers
from .models import Product, ProductImage, RootCategory, MainCategory


class RootCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RootCategory
        fields = "__all__"

class MainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCategory
        fields = "__all__"

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("product", "image")
        
        
class ProductRetrieveSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_image(self, obj):
        """Fetch the first image related to the product, or return None if no images exist."""
        first_image = obj.additionalImages.first()
        return first_image.image.url if first_image else None