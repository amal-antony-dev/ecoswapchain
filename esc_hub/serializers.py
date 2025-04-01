from rest_framework import serializers
from .models import Hub, Route
from esc_user.models import EcoUser


class HubSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = Hub
        fields = ["email", "password", "latitude", "longitude", "hub_type", "district", "state", "pincode"]
        
    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')               

        if EcoUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")
        

        eco_user = EcoUser.objects.create_staffuser(
            email=email,
            password=password,
        )
        
        hub = Hub.objects.create(
            manager=eco_user,
            **validated_data
        )
        
        return hub
    

class HubRetrieveSerializer(serializers.ModelSerializer):
    hubType = serializers.CharField(source="hub_type")
    class Meta:
        model = Hub
        fields = ["id", "latitude", "longitude", "district", "state", "pincode", "hubType"]
        
        
class RouteSerializer(serializers.ModelSerializer):
    to = serializers.SerializerMethodField() # Maps "destination" field from Route
    fromNode = serializers.SerializerMethodField(source="source")  # Maps "source" field from Route

    class Meta:
        model = Route
        fields = ["to", 'fromNode', 'distance', 'time', 'cost']  # Ensure this is a string, not a tuple
        
        
    def get_to(self, obj):
        lList = []
        lList.append(obj.destination.latitude)
        lList.append(obj.destination.longitude)
        return {
            "position": lList,
            "id": obj.destination.id,
            "title": obj.destination.district,
        }
        
    
    def get_fromNode(self, obj):
        lList = []
        lList.append(obj.source.latitude)
        lList.append(obj.source.longitude)        
        return {
            "position": lList,
            "id": obj.source.id,
            "title": obj.source.district,
        }
        
    
