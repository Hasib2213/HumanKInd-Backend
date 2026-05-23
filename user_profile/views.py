from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Return the profile of the currently authenticated user
        return self.request.user.userprofile

class SavedPostsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        from community.models import SavedPost
        return SavedPost.objects.filter(user=self.request.user).order_by('-created_at')
        
    def get_serializer_class(self):
        from community.serializers import SavedPostSerializer
        return SavedPostSerializer

class SavedAffirmationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        from content.models import SavedAffirmation
        return SavedAffirmation.objects.filter(user=self.request.user).order_by('-saved_at')
        
    def get_serializer_class(self):
        from content.serializers import SavedAffirmationSerializer
        return SavedAffirmationSerializer

class SavedMeditationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        from content.models import SavedMeditation
        return SavedMeditation.objects.filter(user=self.request.user).order_by('-saved_at')
        
    def get_serializer_class(self):
        from content.serializers import SavedMeditationSerializer
        return SavedMeditationSerializer

class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        # In Django, deleting the user will cascade and delete associated profile, subscriptions, posts, etc.
        user.delete()
        return Response({'message': 'Account deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required to logout."}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token or token already blacklisted."}, status=status.HTTP_400_BAD_REQUEST)


