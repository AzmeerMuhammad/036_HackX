from django.db import models
from django_cryptography.fields import encrypt
from apps.accounts.models import User


class ChatSession(models.Model):
    """
    Chat session between user and bot/professional.
    Each session can contain multiple messages.
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

