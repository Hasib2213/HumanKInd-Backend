from rest_framework import serializers
from .models import Post, Comment, Like, SavedPost, Report
from Authapp.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'content', 'audio_file', 'is_anonymous', 
            'share_count', 'likes_count', 'comments_count', 
            'is_liked', 'is_saved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'share_count', 'created_at', 'updated_at']

    def get_user(self, obj):
        if obj.is_anonymous:
            return None
        return UserSerializer(obj.user).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saved_by.filter(user=request.user).exists()
        return False

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'post', 'title', 'description', 'created_at']
        read_only_fields = ['created_at']
