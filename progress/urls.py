from django.urls import path
from .views import ProgressOverviewView, MoodLogCreateView, ActivityLogCreateView

urlpatterns = [
    path('', ProgressOverviewView.as_view(), name='progress-overview'),
    path('mood/', MoodLogCreateView.as_view(), name='log-mood'),
    path('activity/', ActivityLogCreateView.as_view(), name='log-activity'),
]
