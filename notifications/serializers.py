from rest_framework import serializers
from .models import Notification, NotificationPreference, DeviceToken
from HumanBackend.serializer_utils import MongoModelSerializer

class NotificationSerializer(MongoModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'created_at']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['push_notifications_enabled']

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['token']
        read_only_fields = ['id', 'created_at']
