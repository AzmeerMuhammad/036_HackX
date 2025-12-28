from rest_framework import serializers
from datetime import timedelta
from .models import JournalEntry


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = (
            'id', 'checkin_mood', 'checkin_intensity', 'text_encrypted',
            'ai_summary', 'sentiment_score', 'sentiment_label', 'intensity_score',
            'key_themes', 'detected_emotions', 'risk_flags', 'suggest_start_chat', 'created_at'
        )
        read_only_fields = (
            'id', 'ai_summary', 'sentiment_score', 'sentiment_label', 'intensity_score',
            'key_themes', 'detected_emotions', 'risk_flags', 'suggest_start_chat', 'created_at'
        )


class JournalEntryCreateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(write_only=True)
    # Note: Voice-to-text is handled in frontend, backend only receives transcribed text
    
    class Meta:
        model = JournalEntry
        fields = (
            'checkin_mood', 'checkin_intensity', 'text'
        )

    def create(self, validated_data):
        text = validated_data.pop('text')
        user = self.context['request'].user
        
        entry = JournalEntry.objects.create(
            user=user,
            text_encrypted=text,
            **validated_data
        )
        
        # Run AI analysis
        from apps.ai.services import analyze_journal
        last_7_days = JournalEntry.objects.filter(
            user=user,
            created_at__gte=entry.created_at - timedelta(days=7)
        ).exclude(id=entry.id)
        
        analysis = analyze_journal(text, last_7_days)
        entry.ai_summary = analysis['ai_summary']
        entry.sentiment_score = float(analysis.get('sentiment_score', 0.0)) if analysis.get('sentiment_score') is not None else None
        entry.sentiment_label = analysis.get('sentiment_label', 'neutral')
        # Use intensity_score from analysis (None for positive sentiment, float for negative/neutral)
        entry.intensity_score = analysis.get('intensity_score')
        entry.key_themes = analysis.get('key_themes', [])
        entry.detected_emotions = analysis.get('detected_emotions', [])
        entry.risk_flags = analysis.get('risk_flags', {})
        entry.suggest_start_chat = analysis.get('suggest_start_chat', False)
        entry.save()
        
        return entry

