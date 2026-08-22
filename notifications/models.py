from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('alert', 'Alert'),
        ('subscription', 'Subscription Alert'),
        ('like', 'Like Alert'),
        ('comment', 'Comment Alert'),
        ('share', 'Share Alert'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title} ({'Read' if self.is_read else 'Unread'})"

class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preference')
    push_notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - Push Enabled: {self.push_notifications_enabled}"

class DeviceToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.email}"

@receiver(post_save, sender=Notification)
def send_push_notification(sender, instance, created, **kwargs):
    if created:
        pref, _ = NotificationPreference.objects.get_or_create(user=instance.user)
        if pref.push_notifications_enabled:
            tokens = DeviceToken.objects.filter(user=instance.user).values_list('token', flat=True)
            if tokens:
                # INTEGRATION POINT: 
                # Here is where you integrate Firebase Admin SDK to actually ping the phone.
                try:
                    from firebase_admin import messaging
                    message = messaging.MulticastMessage(
                        notification=messaging.Notification(title=instance.title, body=instance.message),
                        tokens=list(tokens),
                    )
                    messaging.send_multicast(message)
                    print(f"--> [SUCCESS] Push notification sent to {instance.user.email}: '{instance.title}' to {len(tokens)} device(s).")
                except Exception as e:
                    print(f"--> [ERROR] Failed to send push notification to {instance.user.email}: {e}")
