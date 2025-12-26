from django.contrib import admin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'display_name', 'email', 'is_anonymous_mode', 'is_staff', 'created_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'created_at')

