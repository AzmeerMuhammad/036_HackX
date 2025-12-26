from django.db import models
from django_cryptography.fields import encrypt
from apps.accounts.models import User


class JournalEntry(models.Model):
    """
    Journal entry with encrypted text.
    Note: Voice-to-text is handled in the frontend. The backend receives
    the transcribed text and stores it encrypted.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    checkin_mood = models.CharField(max_length=50, blank=True)
    checkin_intensity = models.FloatField(default=0.0, help_text="0.0 to 1.0")
    
    # Encrypted text field (receives text from frontend, which may come from voice-to-text)
    text_encrypted = encrypt(models.TextField())
    
    # Optional: Store original transcription if frontend sends it separately
    transcription_encrypted = encrypt(models.TextField(blank=True, help_text="Original transcription if different from text"))
    
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

