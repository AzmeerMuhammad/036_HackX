"""
AI analysis service for journal entries.
Uses trained ML models for sentiment and emotion analysis.
Falls back to rule-based analysis if models are unavailable.
"""
import re
from typing import List, Dict, Any

from .model_predictors import get_sentiment_predictor, get_emotion_predictor


def analyze_journal(text: str, last_7_days_entries: List) -> Dict[str, Any]:
    """
    Analyze journal entry text and return AI insights.
    Uses ML models for sentiment and emotion analysis.
    
    Returns:
        - ai_summary: 2-line summary
        - sentiment_score: -1.0 to +1.0
        - sentiment_label: 'positive', 'neutral', or 'negative'
        - intensity_score: 0.0 to 1.0
        - key_themes: list of themes
        - detected_emotions: list of detected emotions (if negative sentiment)
        - risk_flags: dict with risk indicators
        - suggest_start_chat: boolean
    """
    text_lower = text.lower()
    
    # Try to use ML models, fallback to rule-based if unavailable
    sentiment_predictor = get_sentiment_predictor()
    emotion_predictor = get_emotion_predictor()
    
    sentiment_label = None
    sentiment_score = 0.0
    detected_emotions = []
    
    # Use ML sentiment model if available
    if sentiment_predictor:
        try:
            sentiment_label, sentiment_confidence = sentiment_predictor.predict(text)
            
            # Convert sentiment label to score (-1 to +1)
            if sentiment_label.lower() == 'positive':
                sentiment_score = 0.5 + (sentiment_confidence * 0.5)  # 0.5 to 1.0
            elif sentiment_label.lower() == 'negative':
                sentiment_score = -0.5 - (sentiment_confidence * 0.5)  # -1.0 to -0.5
            else:  # neutral
                sentiment_score = (sentiment_confidence - 0.5) * 0.4  # -0.2 to 0.2
            
            # If negative sentiment, use emotion model
            if sentiment_label.lower() == 'negative' and emotion_predictor:
                try:
                    emotion_results = emotion_predictor.predict(text)
                    detected_emotions = [
                        {
                            'emotion': e['emotion'],
                            'confidence': e['confidence']
                        }
                        for e in emotion_results
                    ]
                except Exception as e:
                    print(f"Warning: Emotion prediction failed: {e}")
                    detected_emotions = []
        except Exception as e:
            print(f"Warning: Sentiment prediction failed: {e}")
            sentiment_predictor = None  # Fall through to rule-based
    
    # Fallback to rule-based sentiment analysis if ML model unavailable
    if sentiment_predictor is None:
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
        
        # Determine label from score
        if sentiment_score > 0.2:
            sentiment_label = 'positive'
        elif sentiment_score < -0.2:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
    
    # Intensity analysis (based on intensifiers and exclamation marks)
    intensifiers = ['very', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally', 'really', 'so', 'too']
    intensity_count = sum(1 for word in intensifiers if word in text_lower)
    exclamation_count = text.count('!')
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    
    # Calculate intensity score (always returns a value between 0.0 and 1.0)
    intensity_score = min(1.0, max(0.0, (intensity_count * 0.1 + exclamation_count * 0.05 + caps_ratio * 0.3)))
    
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
    
    # Risk flags (enhanced with emotion model results)
    risk_flags = {
        'self_harm': any(phrase in text_lower for phrase in ['kill myself', 'end it', 'not worth living', 'suicide', 'cut myself', 'hurt myself']) or 
                     any(e['emotion'] == 'suicide intent' for e in detected_emotions),
        'panic': any(word in text_lower for word in ['panic', 'panic attack', 'can\'t breathe', 'heart racing']) or
                 any(e['emotion'] == 'fear' for e in detected_emotions),
        'severe_depression': any(phrase in text_lower for phrase in ['hopeless', 'no point', 'nothing matters', 'give up']) or
                           any(e['emotion'] in ['hopelessness', 'emptiness', 'worthlessness'] for e in detected_emotions),
        'isolation': any(phrase in text_lower for phrase in ['alone', 'no one', 'nobody cares', 'isolated']) or
                    any(e['emotion'] == 'loneliness' for e in detected_emotions),
    }
    
    # 7-day trend analysis
    recent_negative_trend = False
    if last_7_days_entries:
        recent_sentiments = [entry.sentiment_score for entry in last_7_days_entries]
        if len(recent_sentiments) >= 3:
            avg_recent = sum(recent_sentiments) / len(recent_sentiments)
            if sentiment_score < avg_recent - 0.3:  # Significant drop
                recent_negative_trend = True
    
    # Generate 2-line summary (enhanced with emotion model results)
    if sentiment_score > 0.3:
        summary = f"Overall positive mood detected. {', '.join(themes[:2]) if themes else 'General reflection'} noted."
    elif sentiment_score < -0.3:
        if detected_emotions:
            top_emotions = ', '.join([e['emotion'] for e in detected_emotions[:2]])
            summary = f"Challenging emotions expressed. {top_emotions} detected. {', '.join(themes[:2]) if themes else 'Difficult feelings'} identified."
        else:
            summary = f"Challenging emotions expressed. {', '.join(themes[:2]) if themes else 'Difficult feelings'} identified."
    else:
        summary = f"Mixed emotional state. {', '.join(themes[:2]) if themes else 'Various thoughts'} reflected."
    
    # Suggest chat if risk flags or negative trend
    suggest_start_chat = (
        any(risk_flags.values()) or
        (sentiment_score < -0.5 and intensity_score > 0.5) or
        recent_negative_trend
    )
    
    # Ensure intensity_score is always a valid float
    intensity_score = float(intensity_score) if intensity_score is not None else 0.0
    intensity_score = max(0.0, min(1.0, intensity_score))  # Clamp between 0.0 and 1.0
    
    return {
        'ai_summary': summary,
        'sentiment_score': round(float(sentiment_score), 2),
        'sentiment_label': sentiment_label or 'neutral',
        'intensity_score': round(intensity_score, 2),
        'key_themes': themes[:5],  # Top 5 themes
        'detected_emotions': detected_emotions,  # Emotions from ML model (if negative)
        'risk_flags': risk_flags,
        'suggest_start_chat': suggest_start_chat,
    }

