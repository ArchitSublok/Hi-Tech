from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'user_email', 'created_at')
    search_fields = ('full_name', 'phone_number', 'user__email')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'