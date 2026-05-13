from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import UserPreference
from .serializers import UserPreferenceSerializer

class UserPreferenceDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Return the preference for the current user, or create it if it doesn't exist
        obj, created = UserPreference.objects.get_or_create(user=self.request.user)
        return obj

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
