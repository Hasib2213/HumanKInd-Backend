from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Like, SavedPost, Report
from .serializers import PostSerializer, CommentSerializer, ReportSerializer

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id']).order_by('-created_at')

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(user=self.request.user, post=post)

class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            like.delete()
            return Response({"message": "Post unliked", "is_liked": False}, status=status.HTTP_200_OK)
        
        return Response({"message": "Post liked", "is_liked": True}, status=status.HTTP_201_CREATED)

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
        return Response({"message": "Post shared", "share_count": post.share_count}, status=status.HTTP_200_OK)

class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
