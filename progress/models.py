from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class UserStreak(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    most_active_time = models.CharField(max_length=20, default='Morning')

    def __str__(self):
        return f"{self.user.email} - Streak: {self.current_streak}"

class MoodLog(models.Model):
    MOOD_CHOICES = [
        ('Happy', 'Happy'),
        ('Good', 'Good'),
        ('Confident', 'Confident'),
        ('Sad', 'Sad'),
        ('Stressed', 'Stressed'),
        ('Sleepy', 'Sleepy'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_logs')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.mood} at {self.created_at}"

class ActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('calming_session', 'Calming Session'),
        ('mindful_breathing', 'Mindful Breathing'),
        ('affirmation', 'Affirmation'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} at {self.created_at}"
