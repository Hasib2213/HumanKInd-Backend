from django.urls import path
from .views import (
    PostListCreateView, PostDetailView, CommentListCreateView, CommentDetailView,
    LikeToggleView, SaveToggleView, SharePostView, ReportCreateView
)

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<str:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<str:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('posts/<str:post_id>/comments/<str:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('posts/<str:post_id>/like/', LikeToggleView.as_view(), name='like-toggle'),
    path('posts/<str:post_id>/save/', SaveToggleView.as_view(), name='save-toggle'),
    path('posts/<str:post_id>/share/', SharePostView.as_view(), name='share-post'),
    path('reports/', ReportCreateView.as_view(), name='report-create'),
]
