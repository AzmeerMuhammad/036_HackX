"""
AI analysis service for journal entries.
For MVP, uses rule-based analysis with keyword matching.
"""
import re
from typing import List, Dict, Any


def analyze_journal(text: str, last_7_days_entries: List) -> Dict[str, Any]:
    """
    Analyze journal entry text and return AI insights.
    
    Returns:
        - ai_summary: 2-line summary
        - sentiment_score: -1.0 to +1.0
        - intensity_score: 0.0 to 1.0
        - key_themes: list of themes
        - risk_flags: dict with risk indicators
        - suggest_start_chat: boolean
    """
    text_lower = text.lower()
    
    # Sentiment analysis (simple keyword-based)
    positive_words = ['happy', 'joy', 'excited', 'grateful', 'thankful', 'good', 'great', 'wonderful', 'amazing', 'love', 'peace', 'calm', 'relief', 'hope', 'better', 'improving']
    negative_words = ['sad', 'depressed', 'anxious', 'worried', 'fear', 'angry', 'frustrated', 'lonely', 'hopeless', 'tired', 'exhausted', 'pain', 'hurt', 'scared', 'terrified', 'panic', 'overwhelmed']
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Calculate sentiment score
    total_sentiment_words = positive_count + negative_count
    if total_sentiment_words > 0:
        sentiment_score = (positive_count - negative_count) / total_sentiment_words
    else:
        sentiment_score = 0.0
    
    # Normalize to -1 to +1
    sentiment_score = max(-1.0, min(1.0, sentiment_score))
    
    # Intensity analysis (based on intensifiers and exclamation marks)
    intensifiers = ['very', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally', 'really', 'so', 'too']
    intensity_count = sum(1 for word in intensifiers if word in text_lower)
    exclamation_count = text.count('!')
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    
    intensity_score = min(1.0, (intensity_count * 0.1 + exclamation_count * 0.05 + caps_ratio * 0.3))
    
    # Key themes detection
    themes = []
    theme_keywords = {
        'anxiety': ['anxious', 'worry', 'worried', 'nervous', 'panic', 'fear', 'scared'],
        'depression': ['sad', 'depressed', 'down', 'hopeless', 'empty', 'numb', 'worthless'],
        'stress': ['stressed', 'pressure', 'overwhelmed', 'burden', 'tension'],
        'relationships': ['friend', 'family', 'partner', 'relationship', 'love', 'conflict', 'argument'],
        'work': ['work', 'job', 'career', 'boss', 'colleague', 'deadline', 'project'],
        'health': ['health', 'sick', 'pain', 'doctor', 'medication', 'treatment'],
        'sleep': ['sleep', 'insomnia', 'tired', 'exhausted', 'rest', 'wake'],
        'self-harm': ['hurt', 'cut', 'suicide', 'end', 'die', 'kill myself', 'not worth living'],
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            themes.append(theme)
    
    # Risk flags
    risk_flags = {
        'self_harm': any(phrase in text_lower for phrase in ['kill myself', 'end it', 'not worth living', 'suicide', 'cut myself', 'hurt myself']),
        'panic': any(word in text_lower for word in ['panic', 'panic attack', 'can\'t breathe', 'heart racing']),
        'severe_depression': any(phrase in text_lower for phrase in ['hopeless', 'no point', 'nothing matters', 'give up']),
        'isolation': any(phrase in text_lower for phrase in ['alone', 'no one', 'nobody cares', 'isolated']),
    }
    
    # 7-day trend analysis
    recent_negative_trend = False
    if last_7_days_entries:
        recent_sentiments = [entry.sentiment_score for entry in last_7_days_entries]
        if len(recent_sentiments) >= 3:
            avg_recent = sum(recent_sentiments) / len(recent_sentiments)
            if sentiment_score < avg_recent - 0.3:  # Significant drop
                recent_negative_trend = True
    
    # Generate 2-line summary
    if sentiment_score > 0.3:
        summary = f"Overall positive mood detected. {', '.join(themes[:2]) if themes else 'General reflection'} noted."
    elif sentiment_score < -0.3:
        summary = f"Challenging emotions expressed. {', '.join(themes[:2]) if themes else 'Difficult feelings'} identified."
    else:
        summary = f"Mixed emotional state. {', '.join(themes[:2]) if themes else 'Various thoughts'} reflected."
    
    # Suggest chat if risk flags or negative trend
    suggest_start_chat = (
        any(risk_flags.values()) or
        (sentiment_score < -0.5 and intensity_score > 0.5) or
        recent_negative_trend
    )
    
    return {
        'ai_summary': summary,
        'sentiment_score': round(sentiment_score, 2),
        'intensity_score': round(intensity_score, 2),
        'key_themes': themes[:5],  # Top 5 themes
        'risk_flags': risk_flags,
        'suggest_start_chat': suggest_start_chat,
    }

