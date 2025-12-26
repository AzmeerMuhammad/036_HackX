from django.db import models
from django_cryptography.fields import encrypt
from apps.accounts.models import User


class JournalEntry(models.Model):
    """Journal entry with encrypted text and transcription."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    checkin_mood = models.CharField(max_length=50, blank=True)
    checkin_intensity = models.FloatField(default=0.0, help_text="0.0 to 1.0")
    
    # Encrypted fields
    text_encrypted = encrypt(models.TextField())
    transcription_encrypted = encrypt(models.TextField(blank=True))
    
    # Voice file (stored locally in dev)
    voice_file = models.FileField(upload_to='voice_uploads/', blank=True, null=True)
    
    # AI Analysis results
    ai_summary = models.TextField(blank=True)
    sentiment_score = models.FloatField(default=0.0, help_text="-1.0 to +1.0")
    intensity_score = models.FloatField(default=0.0, help_text="0.0 to 1.0")
    key_themes = models.JSONField(default=list, blank=True)
    risk_flags = models.JSONField(default=dict, blank=True)
    suggest_start_chat = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Journal Entries'

    def __str__(self):
        return f"{self.user.display_name} - {self.created_at.date()}"

