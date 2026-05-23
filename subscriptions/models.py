from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100) # e.g. "Annual", "Monthly"
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(help_text="Duration in days (e.g. 30 for monthly, 365 for annual)")
    most_popular = models.BooleanField(default=False)
    trial_days = models.IntegerField(default=0, help_text="Free trial duration in days")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

class UserSubscription(models.Model):
    STATUS_CHOICES = (
        ('pending_payment', 'Pending Payment'),
        ('trialing', 'Trialing'),
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    
    trial_start_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    
    is_canceled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name if self.plan else 'No Plan'} ({self.status})"

    def update_status_if_expired(self):
        changed = False
        if self.status == 'trialing' and self.trial_end_date and timezone.now() > self.trial_end_date:
            self.status = 'expired'
            changed = True
        elif self.status == 'active' and self.current_period_end and timezone.now() > self.current_period_end:
            self.status = 'expired'
            changed = True
        
        if changed:
            self.save(update_fields=['status'])

    def save(self, *args, **kwargs):
        if not self.pk and self.status == 'trialing' and not self.trial_start_date:
            self.trial_start_date = timezone.now()
            trial_days = self.plan.trial_days if (self.plan and hasattr(self.plan, 'trial_days')) else 7
            self.trial_end_date = self.trial_start_date + timedelta(days=trial_days)
        super().save(*args, **kwargs)


class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('initiated', 'Initiated'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_transactions')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_transactions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='BDT')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    gateway_url = models.URLField(blank=True, null=True)
    val_id = models.CharField(max_length=120, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True)
    validation_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"
