from django.urls import path
from .views import (
    DashboardStatsView, UserListView, UserDetailView, UserSuspendView,
    AdminCommunityPostListView, AdminCommunityPostDetailView, AdminUserWarnView,
    AdminSubscriptionPlanUpdateView, AdminSuspendedUsersListView, AdminManagementView, AdminRemoveView,
    AdminPlatformSettingView
)

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(), name='admin_dashboard_stats'),
    path('users/', UserListView.as_view(), name='admin_user_list'),
    path('users/<str:pk>/', UserDetailView.as_view(), name='admin_user_detail'),
    path('users/<str:pk>/suspend/', UserSuspendView.as_view(), name='admin_user_suspend'),
    
    # Phase 2
    path('community/posts/', AdminCommunityPostListView.as_view(), name='admin_community_posts'),
    path('community/posts/<str:pk>/', AdminCommunityPostDetailView.as_view(), name='admin_community_post_detail'),
    path('users/<str:pk>/warn/', AdminUserWarnView.as_view(), name='admin_user_warn'),

    # Phase 3
    path('subscriptions/plans/<str:pk>/', AdminSubscriptionPlanUpdateView.as_view(), name='admin_update_plan'),

    # Phase 4
    path('suspended-users/', AdminSuspendedUsersListView.as_view(), name='admin_suspended_users'),
    path('management/admins/', AdminManagementView.as_view(), name='admin_management'),
    path('management/admins/<str:pk>/', AdminRemoveView.as_view(), name='admin_remove'),

    # Phase 5
    path('settings/platform/', AdminPlatformSettingView.as_view(), name='admin_platform_setting'),
]
