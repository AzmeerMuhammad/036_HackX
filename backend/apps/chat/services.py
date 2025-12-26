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
    Generate bot response following SOP guidelines.
    Returns: {'content': str, 'escalate': bool, 'dangerous_level': bool}
    """
    message_lower = message_text.lower()
    
    # Check for dangerous keywords
    dangerous_keywords = [
        'kill myself', 'suicide', 'end it', 'not worth living',
        'hurt myself', 'cut myself', 'die', 'want to die'
    ]
    
    dangerous_level = any(keyword in message_lower for keyword in dangerous_keywords)
    
    # Get relevant SOP
    sop = get_relevant_sop(message_text)
    
    # Check recent journal risk flags
    recent_journals = JournalEntry.objects.filter(
        user=session.user,
        created_at__gte=timezone.now() - timedelta(days=7)
    )
    has_recent_risk = any(
        any(entry.risk_flags.values()) if isinstance(entry.risk_flags, dict) else False
        for entry in recent_journals
    )
    
    # Generate empathetic response following SOP
    if dangerous_level:
        response = (
            "I'm really concerned about what you're sharing. Your safety is important. "
            "I want to make sure you get the right support. Let me connect you with a professional who can help. "
            "Please know that you're not alone, and there are people who care about you."
        )
        escalate = True
    elif has_recent_risk:
        response = (
            "I hear you, and I want to understand better. Can you tell me more about what you're experiencing? "
            "I'm here to listen and help you find the right support. "
            "What's been on your mind lately?"
        )
        escalate = False
    elif sop:
        # Follow SOP guidance
        if 'anxiety' in sop.category.lower():
            response = (
                "I understand this feels overwhelming. Can you help me understand what's making you feel anxious? "
                "What situations or thoughts trigger these feelings? "
                "Remember, I'm here to listen and support you, not to provide medical advice."
            )
        elif 'depression' in sop.category.lower():
            response = (
                "I hear that you're going through a difficult time. How long have you been feeling this way? "
                "What does a typical day look like for you right now? "
                "I'm here to listen and help you find appropriate support."
            )
        else:
            response = (
                "Thank you for sharing. I want to understand your situation better. "
                "Can you tell me more about what you're experiencing? "
                "What would be most helpful for you right now?"
            )
        escalate = False
    else:
        # Default empathetic response
        response = (
            "I'm here to listen and support you. Can you tell me more about what's on your mind? "
            "What's been challenging for you lately? "
            "Remember, I'm here to gather information and help you find the right support, not to provide medical advice."
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

