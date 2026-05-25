from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription
from HumanBackend.serializer_utils import MongoModelSerializer

class SubscriptionPlanSerializer(MongoModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'description', 'price', 'duration_days', 'most_popular', 'trial_days', 'is_active']

class UserSubscriptionSerializer(MongoModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'plan', 'status', 'trial_start_date', 'trial_end_date', 
            'current_period_start', 'current_period_end', 'is_canceled'
        ]

    def to_representation(self, instance):
        instance.update_status_if_expired()
        return super().to_representation(instance)
