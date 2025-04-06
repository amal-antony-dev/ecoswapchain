from rest_framework import serializers
from .models import Materials, Certification, Product, RootCategory, MainCategory, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'uploaded_at']

    def to_representation(self, instance):
        # Flatten the image URL and rename fields to match the frontend
        return {
            'id': str(instance.id),
            'url': instance.image.url, 
            'alt' : "Product Image",
            # Ensure MEDIA_URL is configured in Django settings
        }

class CertificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Certification
        fields = ['name', 'description', 'certificationNumber']
        
        def to_representation(self, instance):
            return {
            'name': instance.name,
            'description': instance.description,
            'registerNumber': instance.certificationNumber,
        }
            
            
            

class RootCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RootCategory
        fields = ['id', 'name']

class MainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCategory
        fields = ['id', 'name']
        

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materials
        fields = ["name"]
        
          
from rest_framework import serializers
from .models import Product, RootCategory, MainCategory, Materials, Certification, ProductImage

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    rootCategory = serializers.CharField(source="rootCategory.name", read_only=True)
    mainCategory = serializers.CharField(source="mainCategory.name", read_only=True)
    materials = serializers.SerializerMethodField(read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    additionalImages = ProductImageSerializer(many=True, read_only=True)
    
    features = serializers.JSONField()
    condition = serializers.CharField(allow_null=True, allow_blank=True)

    recycledContent = serializers.FloatField(source='recycled_content', allow_null=True)
    recyclability = serializers.BooleanField()
    carbonFootprint = serializers.FloatField(source='carbon_footprint', allow_null=True)
    energyEfficiency = serializers.FloatField(source='energy_efficiency', allow_null=True)
    durability = serializers.IntegerField(allow_null=True)
    repairabilityScore = serializers.FloatField(source='repairability_score', allow_null=True)
    
    ethicalSourcing = serializers.BooleanField(source='ethical_sourcing')
    crueltyFree = serializers.BooleanField(source='cruelity_free')
    plasticFree = serializers.BooleanField(source='plastic_free')
    natural = serializers.BooleanField()
    destructable = serializers.BooleanField()
    hazardous = serializers.BooleanField()

    class Meta:
        model = Product
        fields = [
            "id",
            "rootCategory",
            "mainCategory",
            "materials",
            "certifications",
            "additionalImages",
            "features",
            "condition",
           "recycledContent",
            "recyclability",
            "carbonFootprint",
            "energyEfficiency",
            "durability",
            "repairabilityScore",
            "ethicalSourcing",
            "crueltyFree",
            "plasticFree",
            "natural",
            "destructable",
            "hazardous",
            "owned_from"
        ]
        extra_kwargs = {
            "rootCategory": {"write_only": True},
            "mainCategory": {"write_only": True},
        }

    def get_materials(self, obj):
        return list(obj.materials.values_list("name", flat=True))  # Returns only material names

    def _handle_category(self, category_data, category_model):
        """
        Helper method to handle category creation or retrieval.
        Formats the name to lowercase and uses get_or_create to avoid duplicates.
        """
        if not category_data:
            return None

        category_name = category_data.get("name")
        if not category_name:
            return None

        # Format the name to lowercase for consistency
        category_name = category_name.strip().lower()

        # Use get_or_create to avoid duplicates
        category, created = category_model.objects.get_or_create(name=category_name)
        return category

    def create(self, validated_data):
        # Handle rootCategory
        root_category_data = validated_data.pop("rootCategory", None)
        root_category = self._handle_category(root_category_data, RootCategory)
        if root_category:
            validated_data["rootCategory"] = root_category

        # Handle mainCategory
        main_category_data = validated_data.pop("mainCategory", None)
        main_category = self._handle_category(main_category_data, MainCategory)
        if main_category:
            validated_data["mainCategory"] = main_category

        # Create the product
        product = Product.objects.create(**validated_data)

        return product

    def update(self, instance, validated_data):
        # Handle rootCategory
        root_category_data = validated_data.pop("rootCategory", None)
        root_category = self._handle_category(root_category_data, RootCategory)
        if root_category:
            instance.rootCategory = root_category

        # Handle mainCategory
        main_category_data = validated_data.pop("mainCategory", None)
        main_category = self._handle_category(main_category_data, MainCategory)
        if main_category:
            instance.mainCategory = main_category

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Customize the output to match the exact format needed."""
        representation = super().to_representation(instance)
        
        # Format additionalImages to match ProductImageSerializer's representation
        representation['additionalImages'] = [
            {
                'id': str(image.id),
                'url': image.image.url, 
                'alt': "Product Image"
            }
            for image in instance.additionalImages.all()
        ]
        
        return representation