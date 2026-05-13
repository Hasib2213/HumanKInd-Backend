from rest_framework import serializers
from .models import UserPreference

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['topics', 'tone', 'birth_year', 'obstacles', 'practice_time', 'experience', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_birth_year(self, value):
        import datetime
        current_year = datetime.datetime.now().year
        if value < 1900 or value > current_year:
            raise serializers.ValidationError("Invalid birth year.")
        return value
