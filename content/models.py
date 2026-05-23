from django.db import models
from django.conf import settings

class Affirmation(models.Model):
    text = models.TextField()
    audio_file = models.FileField(upload_to='affirmations/audio/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Affirmation: {self.text[:30]}..."

class SavedAffirmation(models.Model):
    affirmation = models.ForeignKey(Affirmation, on_delete=models.CASCADE, related_name='saved_by')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_affirmations')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('affirmation', 'user')

class Meditation(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='meditations/thumbnails/', blank=True, null=True)
    audio_file = models.FileField(upload_to='meditations/audio/')
    duration = models.CharField(max_length=50, help_text="e.g., '2 Min'")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class SavedMeditation(models.Model):
    meditation = models.ForeignKey(Meditation, on_delete=models.CASCADE, related_name='saved_by')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_meditations')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('meditation', 'user')
