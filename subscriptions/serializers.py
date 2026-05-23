from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'description', 'price', 'duration_days', 'most_popular', 'trial_days', 'is_active']

class UserSubscriptionSerializer(serializers.ModelSerializer):
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
