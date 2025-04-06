from rest_framework import serializers
from .models import Hub, Route, MST, MSTPath
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
    to = serializers.SerializerMethodField()  
    fromNode = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = ["id", "to", "fromNode", "distance", "time", "cost"]

    def get_to(self, obj):
        return {
            "position": [obj.destination.latitude, obj.destination.longitude],
            "id": obj.destination.id,
            "title": obj.destination.district,
        }

    def get_fromNode(self, obj):
        return {
            "position": [obj.source.latitude, obj.source.longitude],
            "id": obj.source.id,
            "title": obj.source.district,
        }


class MSTPathSerializer(serializers.ModelSerializer):
    route = RouteSerializer(many=False)
    class Meta:
        model = MSTPath
        fields = ["id", "route", "number"]
    
class MSTSerializer(serializers.ModelSerializer):
    path = MSTPathSerializer(many=True)
    class Meta:
        model = MST
        fields = "__all__"