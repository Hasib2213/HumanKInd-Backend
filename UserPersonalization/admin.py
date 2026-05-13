from django.contrib import admin
from .models import UserPreference

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'tone', 'birth_year', 'practice_time', 'experience', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_filter = ('tone', 'practice_time', 'experience')
