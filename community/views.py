from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Like, SavedPost, Report, CommentLike
from .serializers import PostSerializer, CommentSerializer, ReportSerializer


def create_notification(user, title, message, notification_type):
    if not user:
        return
    from notifications.models import Notification

    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
    )

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        
        from .models import PostImage, PostVideo
        images = self.request.FILES.getlist('images')
        for img in images:
            PostImage.objects.create(post=post, image=img)
            
        videos = self.request.FILES.getlist('videos')
        for vid in videos:
            PostVideo.objects.create(post=post, video=vid)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Users can only update or delete their own posts
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return Post.objects.filter(user=self.request.user)
        return Post.objects.all()

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post'] = get_object_or_404(Post, id=self.kwargs['post_id'])
        return context

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'], parent__isnull=True).order_by('created_at')

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        parent = serializer.validated_data.get('parent')
        comment = serializer.save(user=self.request.user, post=post)
        
        commenter_name = f"{self.request.user.first_name} {self.request.user.last_name}".strip() or self.request.user.email
        comment_content = serializer.validated_data.get('content', '')
        has_image = bool(serializer.validated_data.get('image'))
        truncated_comment = (comment_content[:50] + '...') if len(comment_content) > 50 else comment_content
        comment_summary = truncated_comment or ('an image' if has_image else 'a comment')

        # Notify post owner if commenter is not the post owner
        if post.user != self.request.user:
            create_notification(
                post.user,
                "New Comment on Your Post",
                f"{commenter_name} commented on your post: \"{comment_summary}\"",
                'comment',
            )

        # Notify the parent comment owner if this is a reply.
        if parent and parent.user != self.request.user:
            create_notification(
                parent.user,
                "New Reply on Your Comment",
                f"{commenter_name} replied to your comment: \"{comment_summary}\"",
                'comment',
            )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post'] = get_object_or_404(Post, id=self.kwargs['post_id'])
        return context

    def get_queryset(self):
        # Users can only update or delete their own comments
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return Comment.objects.filter(user=self.request.user, post_id=self.kwargs.get('post_id'))
        return Comment.objects.filter(post_id=self.kwargs.get('post_id'))

class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            like.delete()
            return Response({"message": "Post unliked", "is_liked": False}, status=status.HTTP_200_OK)
        
        # Notify post owner if liked by someone else
        if post.user != request.user:
            from notifications.models import Notification
            liker_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email
            Notification.objects.create(
                user=post.user,
                title="Post Liked",
                message=f"{liker_name} liked your post.",
                notification_type='like'
            )
        
        return Response({"message": "Post liked", "is_liked": True}, status=status.HTTP_201_CREATED)

class CommentLikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        
        if not created:
            like.delete()
            return Response({"message": "Comment unliked", "is_liked": False}, status=status.HTTP_200_OK)
        
        # Notify comment owner if liked by someone else
        if comment.user != request.user:
            from notifications.models import Notification
            liker_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email
            Notification.objects.create(
                user=comment.user,
                title="Comment Liked",
                message=f"{liker_name} liked your comment.",
                notification_type='like'
            )
        
        return Response({"message": "Comment liked", "is_liked": True}, status=status.HTTP_201_CREATED)

class SaveToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        save, created = SavedPost.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            save.delete()
            return Response({"message": "Post unsaved", "is_saved": False}, status=status.HTTP_200_OK)
        
        return Response({"message": "Post saved", "is_saved": True}, status=status.HTTP_201_CREATED)

class SharePostView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.share_count += 1
        post.save()
        
        # Notify post owner if shared by someone else (authenticated user)
        if request.user.is_authenticated and post.user != request.user:
            from notifications.models import Notification
            sharer_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email
            Notification.objects.create(
                user=post.user,
                title="Post Shared",
                message=f"{sharer_name} shared your post.",
                notification_type='share'
            )
        return Response({"message": "Post shared", "share_count": post.share_count}, status=status.HTTP_200_OK)

class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
