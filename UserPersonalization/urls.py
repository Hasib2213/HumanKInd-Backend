from django.urls import path
from .views import UserPreferenceDetailView

urlpatterns = [
    path('preferences/', UserPreferenceDetailView.as_view(), name='user-preferences'),
]
