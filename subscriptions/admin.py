from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, PaymentTransaction

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'duration_days', 'most_popular', 'trial_days', 'is_active', 'created_at')
    list_display_links = ('id', 'name')
    list_editable = ('price', 'most_popular', 'trial_days', 'is_active')
    list_filter = ('is_active', 'most_popular')
    search_fields = ('name', 'description')
    ordering = ('id',)

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'status', 'trial_start_date', 'trial_end_date', 'current_period_start', 'current_period_end', 'is_canceled')
    list_filter = ('status', 'is_canceled')
    search_fields = ('user__email', 'plan__name')
    ordering = ('id',)


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_id', 'user', 'plan', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'user__email', 'plan__name')
    ordering = ('-created_at',)
