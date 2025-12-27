from django.db import models
from django_cryptography.fields import encrypt
from apps.accounts.models import User


class ChatSession(models.Model):
    """
    Chat session between user and bot/professional.
    Each session can contain multiple messages.
    Enhanced with conversation state, sentiment tracking, and session summary.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='chat_sessions',
        help_text="User participating in this chat session"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='open',
        help_text="Current status of the chat session"
    )
    # Conversation state and context
    conversation_state = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conversation context: topics, sentiment trend, risk trend, asked questions, active SOP category"
    )
    session_summary = models.TextField(
        blank=True,
        help_text="Short bullet summary for professionals, updated as chat progresses"
    )
    sentiment_trend = models.JSONField(
        default=list,
        blank=True,
        help_text="Sentiment scores over time in this session"
    )
    max_risk_score = models.FloatField(
        default=0.0,
        help_text="Highest risk score encountered in this session (0-100)"
    )
    active_sop_categories = models.JSONField(
        default=list,
        blank=True,
        help_text="SOP categories that have been used in this session"
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Whether this chat session is in anonymous mode"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_chatsession'
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Session #{self.id} - {self.user.display_name}"


class ChatMessage(models.Model):
    """
    Encrypted chat message within a chat session.
    Messages are encrypted for privacy.
    Enhanced with sentiment and risk scoring for intelligence.
    """
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('professional', 'Professional'),
    ]
    
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages',
        help_text="Chat session this message belongs to"
    )
    sender = models.CharField(
        max_length=20, 
        choices=SENDER_CHOICES,
        help_text="Who sent this message"
    )
    content_encrypted = encrypt(models.TextField(help_text="Encrypted message content"))
    # Intelligence metadata (for user messages and bot responses)
    sentiment_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Sentiment score for this message (-1.0 to +1.0)"
    )
    risk_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Risk score for this message (0-100)"
    )
    used_sop_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="IDs of SOP documents used to generate bot response (for auditing)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_chatmessage'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]

    def __str__(self):
        return f"{self.sender} - Session #{self.session.id}"

