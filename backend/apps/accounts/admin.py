from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'display_name', 'email', 'is_professional', 'is_staff', 'created_at')
    list_filter = ('is_professional', 'is_staff', 'professional_type')
    search_fields = ('username', 'email', 'display_name')

