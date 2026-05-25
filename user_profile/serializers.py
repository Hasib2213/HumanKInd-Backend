from rest_framework import serializers
from .models import UserProfile
from Authapp.models import User
from HumanBackend.serializer_utils import MongoModelSerializer

class UserProfileSerializer(MongoModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'full_name', 'phone_number', 'location', 'profile_picture']
        read_only_fields = ['id', 'email']
