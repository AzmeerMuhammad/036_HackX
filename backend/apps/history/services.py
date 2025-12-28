"""
History generation and PDF creation services.
"""
from typing import Dict, Any
from apps.journal.models import JournalEntry
from apps.chat.models import ChatSession, ChatMessage
from apps.professionals.models import EscalationTicket
from django.utils import timezone
import json


def generate_history_json(user) -> Dict[str, Any]:
    """Generate comprehensive patient history JSON from all available data."""
    # Get ALL journals (no date filter)
    journals = JournalEntry.objects.filter(
        user=user
    ).order_by('-created_at')
    
    journal_summaries = []
    for journal in journals:
        journal_summaries.append({
            'date': journal.created_at.isoformat(),
            'mood': journal.checkin_mood or 'Not specified',
            'mood_intensity': journal.checkin_intensity or 0.0,
            'summary': journal.ai_summary or '',
            'sentiment_score': journal.sentiment_score or 0.0,
            'sentiment_label': journal.sentiment_label or 'neutral',
            'intensity_score': journal.intensity_score or 0.0,
            'key_themes': journal.key_themes or [],
            'detected_emotions': journal.detected_emotions or [],
            'risk_flags': journal.risk_flags or {},
            'suggest_start_chat': journal.suggest_start_chat,
        })
    
    # Get ALL chat sessions (no date filter)
    chat_sessions = ChatSession.objects.filter(
        user=user
    ).order_by('-created_at')
    
    chat_highlights = []
    for session in chat_sessions:
        message_count = session.messages.count()
        chat_highlights.append({
            'session_id': session.id,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat() if hasattr(session, 'updated_at') else session.created_at.isoformat(),
            'message_count': message_count,
            'session_summary': session.session_summary or '',
            'max_risk_score': session.max_risk_score or 0.0,
            'sentiment_trend': session.sentiment_trend or [],
            'active_sop_categories': session.active_sop_categories or [],
            'is_anonymous': session.is_anonymous,
        })
    
    # Get ALL escalation tickets
    escalations = EscalationTicket.objects.filter(
        user=user
    ).order_by('-created_at')
    
    escalation_summary = []
    for ticket in escalations:
        escalation_summary.append({
            'ticket_id': ticket.id,
            'status': ticket.status or 'pending',
            'verdict': ticket.verdict or 'pending',
            'reason': ticket.reason or '',
            'professional_notes': ticket.professional_notes or '',
            'created_at': ticket.created_at.isoformat(),
            'reviewed_at': ticket.reviewed_at.isoformat() if ticket.reviewed_at else None,
            'assigned_professional': ticket.assigned_professional.user.display_name if ticket.assigned_professional else 'Unassigned',
        })
    
    # Calculate comprehensive trends and statistics
    if journal_summaries:
        sentiment_scores = [j.get('sentiment_score', 0.0) or 0.0 for j in journal_summaries]
        intensity_scores = [j.get('intensity_score', 0.0) or 0.0 for j in journal_summaries]
        mood_intensities = [j.get('mood_intensity', 0.0) or 0.0 for j in journal_summaries]
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        avg_intensity = sum(intensity_scores) / len(intensity_scores) if intensity_scores else 0.0
        avg_mood_intensity = sum(mood_intensities) / len(mood_intensities) if mood_intensities else 0.0
        
        total_risk_flags = sum(1 for j in journal_summaries if j.get('risk_flags') and any(j.get('risk_flags', {}).values()))
        
        # Count sentiment labels
        sentiment_counts = {}
        for j in journal_summaries:
            label = j.get('sentiment_label', 'neutral')
            sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
        
        # Get most common themes
        all_themes = []
        for j in journal_summaries:
            all_themes.extend(j.get('key_themes', []))
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        most_common_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Get date range
        first_entry = journal_summaries[-1] if journal_summaries else None
        last_entry = journal_summaries[0] if journal_summaries else None
    else:
        avg_sentiment = 0.0
        avg_intensity = 0.0
        avg_mood_intensity = 0.0
        total_risk_flags = 0
        sentiment_counts = {}
        most_common_themes = []
        first_entry = None
        last_entry = None
    
    # Calculate chat statistics
    total_chat_messages = sum(s.get('message_count', 0) for s in chat_highlights)
    escalated_sessions = sum(1 for s in chat_highlights if s.get('status') == 'escalated')
    avg_risk_score = sum(s.get('max_risk_score', 0.0) or 0.0 for s in chat_highlights) / len(chat_highlights) if chat_highlights else 0.0
    
    # Get account creation date
    account_created = user.date_joined.isoformat() if hasattr(user, 'date_joined') else None
    
    return {
        'user_id': user.id,
        'display_name': user.display_name or user.username or 'Anonymous',
        'username': user.username,
        'account_created': account_created,
        'generated_at': timezone.now().isoformat(),
        'period': 'all_history',
        'journal_summaries': journal_summaries,
        'chat_highlights': chat_highlights,
        'escalation_summary': escalation_summary,
        'statistics': {
            'total_journal_entries': len(journal_summaries),
            'total_chat_sessions': len(chat_highlights),
            'total_chat_messages': total_chat_messages,
            'total_escalations': len(escalation_summary),
            'escalated_sessions': escalated_sessions,
            'first_entry_date': first_entry.get('date') if first_entry else None,
            'last_entry_date': last_entry.get('date') if last_entry else None,
        },
        'trends': {
            'average_sentiment': round(avg_sentiment, 2),
            'average_intensity': round(avg_intensity, 2),
            'average_mood_intensity': round(avg_mood_intensity, 2),
            'total_risk_flags': total_risk_flags,
            'sentiment_distribution': sentiment_counts,
            'most_common_themes': [{'theme': t[0], 'count': t[1]} for t in most_common_themes],
            'average_chat_risk_score': round(avg_risk_score, 2),
        }
    }

