"""
SOP-driven chatbot service.
Chatbot follows SOP documents and never gives medical advice.
"""
from typing import Dict, List, Optional
from django.db import models
from .models import ChatSession, ChatMessage
from apps.professionals.models import ProfessionalSOPDoc, Professional, EscalationTicket
from apps.journal.models import JournalEntry
from django.utils import timezone
from datetime import timedelta


def get_relevant_sop(message_text: str) -> Optional[ProfessionalSOPDoc]:
    """Get relevant SOP document based on message content."""
    message_lower = message_text.lower()
    
    # Simple keyword matching for MVP
    category_keywords = {
        'anxiety': ['anxious', 'worry', 'nervous', 'panic', 'fear'],
        'depression': ['sad', 'depressed', 'down', 'hopeless', 'empty'],
        'self-harm-risk': ['hurt', 'suicide', 'kill', 'end', 'die'],
        'panic': ['panic', 'attack', 'breathing', 'heart racing'],
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            sop = ProfessionalSOPDoc.objects.filter(
                category=category,
                active=True
            ).first()
            if sop:
                return sop
    
    # Default SOP
    return ProfessionalSOPDoc.objects.filter(active=True).first()


def generate_bot_response(message_text: str, session: ChatSession, conversation_history: List[ChatMessage]) -> Dict[str, any]:
    """
    Generate empathetic bot response for history gathering using AI.
    Returns: {'content': str, 'escalate': bool, 'dangerous_level': bool}
    """
    message_lower = message_text.lower()

    # Check for dangerous keywords
    dangerous_keywords = [
        'kill myself', 'suicide', 'end it', 'not worth living',
        'hurt myself', 'cut myself', 'die', 'want to die'
    ]

    dangerous_level = any(keyword in message_lower for keyword in dangerous_keywords)

    # Check recent journal risk flags
    recent_journals = JournalEntry.objects.filter(
        user=session.user,
        created_at__gte=timezone.now() - timedelta(days=7)
    )
    has_recent_risk = any(
        any(entry.risk_flags.values()) if isinstance(entry.risk_flags, dict) else False
        for entry in recent_journals
    )

    # Handle dangerous/crisis situations with immediate escalation
    if dangerous_level:
        response = (
            "I'm really concerned about what you're sharing. Your safety is important. "
            "I want to make sure you get the right support. Let me connect you with a professional who can help. "
            "Please know that you're not alone, and there are people who care about you."
        )
        escalate = True
    else:
        # Use AI service for empathetic history gathering
        try:
            from utils.ai_service import ai_service

            # Build conversation history for AI
            ai_conversation_history = []
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                ai_conversation_history.append({
                    'role': 'user' if msg.sender == 'user' else 'assistant',
                    'content': msg.content_encrypted
                })

            # Get summary of recent journals for context
            journals_summary = None
            if recent_journals.exists():
                journal_themes = []
                for entry in recent_journals[:5]:  # Last 5 journals
                    if entry.key_themes:
                        journal_themes.extend(entry.key_themes)
                if journal_themes:
                    journals_summary = ', '.join(set(journal_themes))

            # Get AI response
            response = ai_service.get_history_chat_response(
                user_message=message_text,
                conversation_history=ai_conversation_history,
                user_journals_summary=journals_summary
            )
            escalate = False

        except Exception as e:
            print(f"Warning: AI service failed, using fallback: {e}")
            # Fallback to rule-based response
            if has_recent_risk:
                response = (
                    "I hear you, and I want to understand better. Can you tell me more about what you're experiencing? "
                    "I'm here to listen and help you find the right support. "
                    "What's been on your mind lately?"
                )
            else:
                response = (
                    "I'm here to listen and support you. Can you tell me more about what's on your mind? "
                    "What's been challenging for you lately? "
                    "Remember, I'm here to gather your history and help you find the right support."
                )
            escalate = False

    return {
        'content': response,
        'escalate': escalate,
        'dangerous_level': dangerous_level,
    }


def assign_professional(user) -> Optional[Professional]:
    """Assign a professional using round-robin or first available."""
    professionals = Professional.objects.filter(verified=True)
    if not professionals.exists():
        return None
    
    # Simple round-robin: get professional with least pending tickets
    from django.db.models import Count
    professionals_with_counts = professionals.annotate(
        pending_count=Count('assigned_tickets', filter=models.Q(assigned_tickets__status='pending'))
    ).order_by('pending_count', 'id')
    
    return professionals_with_counts.first()


def create_escalation_ticket(session: ChatSession, reason: str):
    """Create escalation ticket and assign to professional."""
    professional = assign_professional(session.user)
    if not professional:
        return None
    
    ticket = EscalationTicket.objects.create(
        session=session,
        user=session.user,
        assigned_professional=professional,
        reason=reason,
        status='pending'
    )
    
    session.status = 'escalated'
    session.save()
    
    return ticket

