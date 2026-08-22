from rest_framework import serializers
from .models import Affirmation, SavedAffirmation, Meditation, SavedMeditation, JournalEntry
from HumanBackend.serializer_utils import MongoModelSerializer
from Authapp.serializers import UserSerializer

class AffirmationSerializer(MongoModelSerializer):
    class Meta:
        model = Affirmation
        fields = ['id', 'text', 'audio_file', 'created_at']

class SavedAffirmationSerializer(MongoModelSerializer):
    affirmation = AffirmationSerializer(read_only=True)
    
    class Meta:
        model = SavedAffirmation
        fields = ['id', 'affirmation', 'saved_at']

class MeditationSerializer(MongoModelSerializer):
    class Meta:
        model = Meditation
        fields = ['id', 'title', 'description', 'thumbnail', 'audio_file', 'duration', 'created_at']

class SavedMeditationSerializer(MongoModelSerializer):
    meditation = MeditationSerializer(read_only=True)
    
    class Meta:
        model = SavedMeditation
        fields = ['id', 'meditation', 'saved_at']

class JournalEntrySerializer(MongoModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = JournalEntry
        fields = ['id', 'user', 'question', 'prompt', 'ai_response', 'created_at']
