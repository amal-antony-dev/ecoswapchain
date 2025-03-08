from rest_framework import serializers
from esc_user.models import EcoUser  # Import the EcoUser model

class EcoUserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoUser
        fields = ["id", "first_name", "last_name", "role"]  # Include the fields you need


