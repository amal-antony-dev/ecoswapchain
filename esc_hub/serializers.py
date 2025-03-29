from rest_framework import serializers
from .models import Hub
from esc_user.models import EcoUser


class HubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = ["email", "password", "latitude", "longitude", "hub_type"]
        
    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')               

        if EcoUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")
        

        eco_user = EcoUser.objects.create_user(
            email=email,
            password=password,
            role=EcoUser.shipping
        )
        
        hub = Hub.objects.create(
            eco_user=eco_user,
            **validated_data
        )
        
        return hub