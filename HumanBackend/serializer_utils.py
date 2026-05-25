from django_mongodb_backend.fields import ObjectIdAutoField
from rest_framework import serializers


class MongoPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        if value is None:
            return None
        return str(value.pk)


class MongoModelSerializer(serializers.ModelSerializer):
    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        ObjectIdAutoField: serializers.CharField,
    }
