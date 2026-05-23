from rest_framework import serializers
from .models import Affirmation, SavedAffirmation, Meditation, SavedMeditation

class AffirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affirmation
        fields = ['id', 'text', 'audio_file', 'created_at']

class SavedAffirmationSerializer(serializers.ModelSerializer):
    affirmation = AffirmationSerializer(read_only=True)
    
    class Meta:
        model = SavedAffirmation
        fields = ['id', 'affirmation', 'saved_at']

class MeditationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meditation
        fields = ['id', 'title', 'description', 'thumbnail', 'audio_file', 'duration', 'created_at']

class SavedMeditationSerializer(serializers.ModelSerializer):
    meditation = MeditationSerializer(read_only=True)
    
    class Meta:
        model = SavedMeditation
        fields = ['id', 'meditation', 'saved_at']
