from rest_framework import serializers
from esc_user.models import EcoUser  
from .models import Trader

class TraderRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)

    class Meta:
        model = Trader
        fields = ['email', 'password', 'first_name', 'last_name', 'username']

    def create(self, validated_data):
        # Extract user-related data
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        username = validated_data.pop('username')                

        if EcoUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")
        
        if EcoUser.objects.filter(username=username).exists():
            raise serializers.ValidationError("User with this username already exists")

        # Create user (EcoUser extending AbstractUser)
        eco_user = EcoUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username,
            role=EcoUser.trader
        )

        # Create Trader instance
        trader = Trader.objects.create(
            eco_user=eco_user,
            verified=True
        )

        return trader 