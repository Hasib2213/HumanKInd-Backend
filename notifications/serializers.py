from rest_framework import serializers
from .models import Notification
from HumanBackend.serializer_utils import MongoModelSerializer

class NotificationSerializer(MongoModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
