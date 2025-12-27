from django.db import models
from django_cryptography.fields import encrypt
from apps.accounts.models import User


class JournalEntry(models.Model):
    """
    Journal entry with encrypted text.
    Note: Voice-to-text is handled in the frontend. The backend receives
    the transcribed text and stores it encrypted.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='journal_entries',
        help_text="User who created this journal entry"
    )
    checkin_mood = models.CharField(max_length=50, blank=True, help_text="User's mood at time of entry")
    checkin_intensity = models.FloatField(default=0.0, help_text="Mood intensity: 0.0 to 1.0")
    
    # Encrypted text field (receives text from frontend, which may come from voice-to-text)
    text_encrypted = encrypt(models.TextField(help_text="Encrypted journal entry text"))
    
    # Optional: Store original transcription if frontend sends it separately
    transcription_encrypted = encrypt(models.TextField(
        blank=True, 
        help_text="Original transcription if different from text"
    ))
    
    # AI Analysis results
    ai_summary = models.TextField(blank=True, help_text="AI-generated summary of the entry")
    sentiment_score = models.FloatField(default=0.0, help_text="Sentiment: -1.0 (negative) to +1.0 (positive)")
    sentiment_label = models.CharField(max_length=20, default='neutral', help_text="Sentiment label: positive, neutral, or negative")
    intensity_score = models.FloatField(default=0.0, help_text="Emotional intensity: 0.0 to 1.0")
    key_themes = models.JSONField(default=list, blank=True, help_text="List of key themes identified")
    detected_emotions = models.JSONField(default=list, blank=True, help_text="List of detected emotions with confidence scores")
    risk_flags = models.JSONField(default=dict, blank=True, help_text="Risk flags detected (e.g., suicidal_ideation)")
    suggest_start_chat = models.BooleanField(default=False, help_text="AI suggests starting a chat session")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'journal_journalentry'
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.display_name} - {self.created_at.date()}"

