from django.db import models

class PlatformSetting(models.Model):
    # Contact Support
    location = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    x_profile_link = models.URLField(blank=True, null=True)
    instagram_profile_link = models.URLField(blank=True, null=True)
    facebook_profile_link = models.URLField(blank=True, null=True)

    # Privacy & Safety
    privacy_policy = models.TextField(blank=True, null=True)

    # About GLOW
    about_glow = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Enforce Singleton pattern: ensure only one row exists
        if self._state.adding and PlatformSetting.objects.exists():
            raise ValueError('There can be only one PlatformSetting instance')
        super(PlatformSetting, self).save(*args, **kwargs)

    def __str__(self):
        return "Global Platform Settings"
