from rest_framework import serializers
from .models import UserPreference

class UserPreferenceSerializer(serializers.ModelSerializer):
    topics = serializers.MultipleChoiceField(choices=UserPreference.TOPIC_CHOICES, required=False)
    obstacles = serializers.MultipleChoiceField(choices=UserPreference.OBSTACLE_CHOICES, required=False)
    
    class Meta:
        model = UserPreference
        fields = ['topics', 'tone', 'birth_year', 'obstacles', 'practice_time', 'experience', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        if 'topics' in ret:
            ret['topics'] = list(ret['topics'])
        if 'obstacles' in ret:
            ret['obstacles'] = list(ret['obstacles'])
        return ret

    def validate_birth_year(self, value):
        import datetime
        current_year = datetime.datetime.now().year
        if value < 1900 or value > current_year:
            raise serializers.ValidationError("Invalid birth year.")
        return value
