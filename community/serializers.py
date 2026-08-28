from rest_framework import serializers
from .models import Post, Comment, Like, SavedPost, Report, PostImage, PostVideo
from Authapp.serializers import UserSerializer
from HumanBackend.serializer_utils import MongoModelSerializer, MongoPrimaryKeyRelatedField

class CommentSerializer(MongoModelSerializer):
    user = UserSerializer(read_only=True)
    parent = MongoPrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'parent', 'content', 'image', 'video', 'replies', 'created_at', 'likes_count', 'is_liked', 'liked_by']

    def validate_parent(self, value):
        post = self.context.get('post')
        if value and post and value.post_id != post.id:
            raise serializers.ValidationError('Reply must belong to the same post.')
        return value

    def validate(self, attrs):
        content = (attrs.get('content') or '').strip()
        image = attrs.get('image')
        video = attrs.get('video')

        if not content and not image and not video:
            raise serializers.ValidationError('Comment must include text, an image, or a video.')

        return attrs

    def get_replies(self, obj):
        replies = obj.replies.select_related('user', 'parent').order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_liked_by(self, obj):
        likers = obj.likes.select_related('user').order_by('-created_at')
        return [UserSerializer(like.user).data for like in likers]

class PostImageSerializer(MongoModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'created_at']

class PostVideoSerializer(MongoModelSerializer):
    class Meta:
        model = PostVideo
        fields = ['id', 'video', 'created_at']

class PostSerializer(MongoModelSerializer):
    user = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)
    videos = PostVideoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'content', 'audio_file', 'images', 'videos', 'is_anonymous', 
            'share_count', 'likes_count', 'comments_count', 
            'is_liked', 'is_saved', 'liked_by', 'comments', 'created_at', 'updated_at'
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

    def get_liked_by(self, obj):
        likers = obj.likes.select_related('user').order_by('-created_at')
        return [UserSerializer(like.user).data for like in likers]

    def get_comments(self, obj):
        root_comments = obj.comments.filter(parent__isnull=True).select_related('user', 'parent').order_by('created_at')
        return CommentSerializer(root_comments, many=True, context=self.context).data

class ReportSerializer(MongoModelSerializer):
    post = MongoPrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Report
        fields = ['id', 'post', 'title', 'description', 'created_at']
        read_only_fields = ['created_at']

class SavedPostSerializer(MongoModelSerializer):
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = SavedPost
        fields = ['id', 'post', 'created_at']
