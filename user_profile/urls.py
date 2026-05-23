from django.urls import path
from .views import UserProfileView, SavedPostsView, SavedAffirmationsView, SavedMeditationsView, DeleteAccountView, LogoutView

urlpatterns = [
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('saved/posts/', SavedPostsView.as_view(), name='saved-posts'),
    path('saved/affirmations/', SavedAffirmationsView.as_view(), name='saved-affirmations'),
    path('saved/meditations/', SavedMeditationsView.as_view(), name='saved-meditations'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
