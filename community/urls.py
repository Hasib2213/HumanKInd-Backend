from django.urls import path
from .views import (
    PostListCreateView, PostDetailView, CommentListCreateView,
    LikeToggleView, SaveToggleView, SharePostView, ReportCreateView
)

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('posts/<int:post_id>/like/', LikeToggleView.as_view(), name='like-toggle'),
    path('posts/<int:post_id>/save/', SaveToggleView.as_view(), name='save-toggle'),
    path('posts/<int:post_id>/share/', SharePostView.as_view(), name='share-post'),
    path('reports/', ReportCreateView.as_view(), name='report-create'),
]
