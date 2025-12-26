from django.db import models
from django_cryptography.fields import encrypt
from apps.accounts.models import User


class ChatSession(models.Model):
    """Chat session between user and bot/professional."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Session #{self.id} - {self.user.display_name}"


class ChatMessage(models.Model):
    """Encrypted chat message."""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('professional', 'Professional'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    content_encrypted = encrypt(models.TextField())
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender} - {self.session.id}"

