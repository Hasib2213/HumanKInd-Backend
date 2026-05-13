from django.db import models
from django.conf import settings

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='personalization')
    
    # Topics of interest (Stored as JSON or comma-separated string)
    topics = models.JSONField(default=list, help_text="List of topics of interest")
    
    # Personalize tone
    TONE_CHOICES = [
        ('gentle', 'Gentle & Nurturing'),
        ('bold', 'Bold & Empowering'),
        ('spiritual', 'Spiritual and Mindful'),
    ]
    tone = models.CharField(max_length=20, choices=TONE_CHOICES)
    
    # Birth Year
    birth_year = models.IntegerField(null=True, blank=True)
    
    # Obstacles
    obstacles = models.JSONField(default=list, help_text="What prevents you from achieving results?")
    
    # Practice Time
    PRACTICE_CHOICES = [
        ('5min', '5 minutes a day'),
        ('10min', '10 minutes a day'),
        ('20min', '20 minutes a day'),
    ]
    practice_time = models.CharField(max_length=10, choices=PRACTICE_CHOICES)
    
    # Meditation Experience
    EXPERIENCE_CHOICES = [
        ('beginner', "I'm a total beginner"),
        ('few_times', "I've meditated a few times"),
        ('a_lot', "I meditate a lot"),
    ]
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Personalization for {self.user.email}"
