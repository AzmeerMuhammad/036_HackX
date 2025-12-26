from django.contrib import admin
from .models import ConsentGrant


@admin.register(ConsentGrant)
class ConsentGrantAdmin(admin.ModelAdmin):
    list_display = ('user', 'professional', 'active', 'created_at')
    list_filter = ('active', 'created_at')

