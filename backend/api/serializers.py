from .models import CustomUser
from rest_framework import serializers

DEFAULT_CHIPS = 1000

class RegisterSerialier(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'chips']
        read_only_fields = ['chips']
        
    def create(self, validated_data):
        return CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            chips=DEFAULT_CHIPS
        )
