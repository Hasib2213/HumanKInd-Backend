from django.urls import path

from .views import DailyAffirmationView, AIMeditationView, JournalView

urlpatterns = [
    path('daily-affirmation/', DailyAffirmationView.as_view(), name='daily-affirmation'),
    path('ai-meditation/', AIMeditationView.as_view(), name='ai-meditation'),
    path('journal/', JournalView.as_view(), name='journal'),
]