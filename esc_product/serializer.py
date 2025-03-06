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
            'url': instance.image.url,  # Ensure MEDIA_URL is configured in Django settings
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
        
          
class ProductSerializer(serializers.ModelSerializer):
    rootCategory = serializers.CharField(source="rootCategory.name", read_only=True)
    mainCategory = serializers.CharField(source="mainCategory.name", read_only=True)
    materials = serializers.SerializerMethodField(read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    additionalImages = ProductImageSerializer(many=True, read_only=True)
    recycledContent = serializers.FloatField(source='recycled_content')
    carbonFootprint = serializers.FloatField(source='carbon_footprint')
    energyEfficiency = serializers.FloatField(source='energy_efficiency')
    repairabilityScore = serializers.FloatField(source='repairability_score')
    ethicalSourcing = serializers.BooleanField(source='ethical_sourcing')
    crueltyFree = serializers.BooleanField(source='cruelity_free')
    plasticFree = serializers.BooleanField(source='plastic_free')
    additionalMaterials = serializers.JSONField(source='additional_materials')

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'rootCategory': {'write_only': True},
            'mainCategory': {'write_only': True},
        }
        
    def get_materials(self, obj):
        return list(obj.materials.values_list("name", flat=True))  # Returns only names

    def _handle_category(self, category_data, category_model):
        """
        Helper method to handle category creation or retrieval.
        Formats the name to lowercase and uses get_or_create to avoid duplicates.
        """
        if not category_data:
            return None

        category_name = category_data.get('name')
        if not category_name:
            return None

        # Format the name to lowercase for consistency
        category_name = category_name.strip().lower()

        # Use get_or_create to avoid duplicates
        category, created = category_model.objects.get_or_create(name=category_name)
        return category

    def create(self, validated_data):
        # Handle rootCategory
        root_category_data = validated_data.pop('rootCategory', None)
        root_category = self._handle_category(root_category_data, RootCategory)
        if root_category:
            validated_data['rootCategory'] = root_category

        # Handle mainCategory
        main_category_data = validated_data.pop('mainCategory', None)
        main_category = self._handle_category(main_category_data, MainCategory)
        if main_category:
            validated_data['mainCategory'] = main_category
            
        

        # Create the product
        product = Product.objects.create(**validated_data)
        
        return product

    def update(self, instance, validated_data):
        # Handle rootCategory
        root_category_data = validated_data.pop('rootCategory', None)
        root_category = self._handle_category(root_category_data, RootCategory)
        if root_category:
            instance.root_category = root_category

        # Handle mainCategory
        main_category_data = validated_data.pop('mainCategory', None)
        main_category = self._handle_category(main_category_data, MainCategory)
        if main_category:
            instance.main_category = main_category

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance





