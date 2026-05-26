from rest_framework import serializers
from .models import UserProfile
from Authapp.models import User
from HumanBackend.serializer_utils import MongoModelSerializer

class UserProfileSerializer(MongoModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, required=False)
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, required=False)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'phone_number', 'location', 'profile_picture']
        read_only_fields = ['id', 'email']

    def update(self, instance, validated_data):
        # Handle nested user fields (first_name, last_name)
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            changed = False
            for attr, value in user_data.items():
                if getattr(user, attr, None) != value:
                    setattr(user, attr, value)
                    changed = True
            if changed:
                user.save()

        return super().update(instance, validated_data)
