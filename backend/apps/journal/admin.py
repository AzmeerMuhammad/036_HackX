from django.contrib import admin
from .models import JournalEntry


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'sentiment_score', 'intensity_score', 'suggest_start_chat')
    list_filter = ('suggest_start_chat', 'created_at')
    search_fields = ('user__username', 'ai_summary')
    readonly_fields = ('text_encrypted', 'transcription_encrypted', 'created_at')

