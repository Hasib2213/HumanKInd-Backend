from rest_framework import serializers
from .models import PlatformSetting

class PlatformSettingSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    
    class Meta:
        model = PlatformSetting
        fields = '__all__'
