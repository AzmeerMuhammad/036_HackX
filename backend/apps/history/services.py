"""
History generation and PDF creation services.
"""
from typing import Dict, Any
from apps.journal.models import JournalEntry
from apps.chat.models import ChatSession, ChatMessage
from apps.professionals.models import EscalationTicket
from django.utils import timezone
from datetime import timedelta
import json


def generate_history_json(user) -> Dict[str, Any]:
    """Generate patient history JSON from last 7 days."""
    # Get last 7 days of journals
    journals = JournalEntry.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')
    
    journal_summaries = []
    for journal in journals:
        journal_summaries.append({
            'date': journal.created_at.isoformat(),
            'summary': journal.ai_summary,
            'sentiment_score': journal.sentiment_score,
            'intensity_score': journal.intensity_score,
            'key_themes': journal.key_themes,
            'risk_flags': journal.risk_flags,
        })
    
    # Get chat sessions
    chat_sessions = ChatSession.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')
    
    chat_highlights = []
    for session in chat_sessions:
        messages = session.messages.all()[:5]  # First 5 messages
        chat_highlights.append({
            'session_id': session.id,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'message_count': session.messages.count(),
        })
    
    # Get escalation tickets
    escalations = EscalationTicket.objects.filter(
        user=user
    ).order_by('-created_at')
    
    escalation_summary = []
    for ticket in escalations:
        escalation_summary.append({
            'ticket_id': ticket.id,
            'status': ticket.status,
            'verdict': ticket.verdict,
            'created_at': ticket.created_at.isoformat(),
        })
    
    # Calculate trends
    if journal_summaries:
        avg_sentiment = sum(j['sentiment_score'] for j in journal_summaries) / len(journal_summaries)
        avg_intensity = sum(j['intensity_score'] for j in journal_summaries) / len(journal_summaries)
        total_risk_flags = sum(1 for j in journal_summaries if any(j.get('risk_flags', {}).values()))
    else:
        avg_sentiment = 0.0
        avg_intensity = 0.0
        total_risk_flags = 0
    
    return {
        'user_id': user.id,
        'display_name': user.display_name,
        'generated_at': timezone.now().isoformat(),
        'period': '7_days',
        'journal_summaries': journal_summaries,
        'chat_highlights': chat_highlights,
        'escalation_summary': escalation_summary,
        'trends': {
            'average_sentiment': round(avg_sentiment, 2),
            'average_intensity': round(avg_intensity, 2),
            'total_risk_flags': total_risk_flags,
            'total_journal_entries': len(journal_summaries),
            'total_chat_sessions': len(chat_highlights),
        }
    }

