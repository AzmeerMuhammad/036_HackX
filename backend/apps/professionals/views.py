from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Professional, EscalationTicket
from .serializers import (
    ProfessionalSerializer, ProfessionalApplySerializer, 
    EscalationTicketSerializer, EscalationVerdictSerializer
)


class ProfessionalListView(generics.ListAPIView):
    """List all professionals (public)."""
    queryset = Professional.objects.filter(verified=True).order_by('-created_at')
    permission_classes = [permissions.AllowAny]
    serializer_class = ProfessionalSerializer
    pagination_class = None  # Disable pagination to show all professionals


class ProfessionalApplyView(generics.CreateAPIView):
    """Apply to become a professional or update existing profile."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfessionalApplySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        professional = serializer.save()
        
        # Return response with verification status
        response_data = ProfessionalSerializer(professional).data
        if professional.verified:
            response_data['message'] = 'Profile complete! You are now verified and visible to users.'
        else:
            response_data['message'] = 'Profile updated. Please complete all required fields to be verified.'
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def professional_profile(request):
    """Get or update current user's professional profile."""
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        return Response(
            {'error': 'You are not a professional. Please apply first.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = ProfessionalSerializer(professional)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProfessionalApplySerializer(
            professional, 
            data=request.data, 
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        professional = serializer.save()
        
        response_data = ProfessionalSerializer(professional).data
        if professional.verified:
            response_data['message'] = 'Profile complete! You are now verified and visible to users.'
        else:
            missing = professional.get_missing_fields()
            response_data['message'] = f'Please complete: {", ".join(missing)}'
        
        return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_professional(request):
    """Submit verification documents for professional identity verification."""
    try:
        professional = request.user.professional_profile
    except Professional.DoesNotExist:
        return Response(
            {'error': 'You are not a professional. Please sign up as a professional first.'},
            status=status.HTTP_404_NOT_FOUND
        )

    professional_type = request.data.get('professional_type')
    if not professional_type or professional_type not in ['psychiatrist', 'therapist', 'psychologist']:
        return Response(
            {'error': 'Please select a valid professional type'},
            status=status.HTTP_400_BAD_REQUEST
        )

    professional.professional_type = professional_type

    if professional_type == 'psychiatrist':
        pmdc_id = request.data.get('pmdc_id')
        if not pmdc_id:
            return Response(
                {'error': 'PMDC ID is required for psychiatrists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        professional.pmdc_id = pmdc_id
    else:  # therapist or psychologist
        degree_picture = request.FILES.get('degree_picture')
        university_name = request.data.get('university_name')

        if not degree_picture:
            return Response(
                {'error': 'Degree picture is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not university_name:
            return Response(
                {'error': 'University name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        professional.degree_picture = degree_picture
        professional.university_name = university_name

    professional.save()

    return Response({
        'message': 'Verification successful! You now have full access to the dashboard.',
        'verified': professional.verified,
        'professional_type': professional.professional_type
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_escalations(request):
    """Get user's escalation tickets."""
    tickets = EscalationTicket.objects.filter(user=request.user).order_by('-created_at')
    serializer = EscalationTicketSerializer(tickets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def professional_escalations(request):
    """Get escalation tickets assigned to the authenticated professional."""
    try:
        professional = request.user.professional_profile
        if not professional.verified:
            return Response(
                {'error': 'Only verified professionals can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
    except Professional.DoesNotExist:
        return Response(
            {'error': 'You are not a professional'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    tickets = EscalationTicket.objects.filter(
        assigned_professional=professional,
        status='pending'
    ).order_by('-created_at')
    serializer = EscalationTicketSerializer(tickets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def professional_escalation_detail(request, ticket_id):
    """Get escalation ticket detail."""
    try:
        professional = request.user.professional_profile
        if not professional.verified:
            return Response(
                {'error': 'Only verified professionals can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
    except Professional.DoesNotExist:
        return Response(
            {'error': 'You are not a professional'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    ticket = get_object_or_404(
        EscalationTicket,
        id=ticket_id,
        assigned_professional=professional
    )
    serializer = EscalationTicketSerializer(ticket)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def professional_escalation_verdict(request, ticket_id):
    """Submit verdict for an escalation ticket."""
    try:
        professional = request.user.professional_profile
        if not professional.verified:
            return Response(
                {'error': 'Only verified professionals can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
    except Professional.DoesNotExist:
        return Response(
            {'error': 'You are not a professional'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    ticket = get_object_or_404(
        EscalationTicket,
        id=ticket_id,
        assigned_professional=professional,
        status='pending'
    )
    
    serializer = EscalationVerdictSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    ticket.verdict = serializer.validated_data['verdict']
    ticket.professional_notes = serializer.validated_data.get('professional_notes', '')
    ticket.status = 'reviewed'
    from django.utils import timezone
    ticket.reviewed_at = timezone.now()
    ticket.save()
    
    return Response(EscalationTicketSerializer(ticket).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def professional_patients(request):
    """Get list of patients who have granted consent to the authenticated professional."""
    try:
        professional = request.user.professional_profile
        if not professional.verified:
            return Response(
                {'error': 'Only verified professionals can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
    except Professional.DoesNotExist:
        return Response(
            {'error': 'You are not a professional'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get all active consent grants for this professional
    from apps.consent.models import ConsentGrant
    from apps.journal.models import JournalEntry
    from django.db.models import Count, Max
    
    consents = ConsentGrant.objects.filter(
        professional=professional,
        active=True
    ).select_related('user')
    
    patients_data = []
    for consent in consents:
        user = consent.user
        
        # Get journal entry stats
        journal_stats = JournalEntry.objects.filter(user=user).aggregate(
            entries_count=Count('id'),
            last_entry=Max('created_at')
        )
        
        # Get latest journal entry for risk level
        latest_entry = JournalEntry.objects.filter(user=user).order_by('-created_at').first()
        
        # Determine risk level based on latest entry
        risk_level = 'low'
        if latest_entry:
            if latest_entry.suggest_start_chat or latest_entry.risk_flags:
                # Check for high-risk flags
                if isinstance(latest_entry.risk_flags, dict):
                    high_risk_flags = ['suicidal_ideation', 'self_harm', 'crisis', 'self-harm', 'suicidal']
                    if any(flag in str(latest_entry.risk_flags).lower() for flag in high_risk_flags):
                        risk_level = 'high'
                    elif latest_entry.sentiment_score < -0.5 or latest_entry.intensity_score > 0.8:
                        risk_level = 'medium'
                    else:
                        risk_level = 'low'
                elif latest_entry.sentiment_score < -0.5 or latest_entry.intensity_score > 0.8:
                    risk_level = 'medium'
        
        patients_data.append({
            'id': user.id,
            'name': user.display_name or user.username,
            'email': user.email or '',
            'sharedSince': consent.created_at.isoformat(),
            'lastEntry': journal_stats['last_entry'].isoformat() if journal_stats['last_entry'] else None,
            'entriesCount': journal_stats['entries_count'] or 0,
            'riskLevel': risk_level,
            'summaryAvailable': journal_stats['entries_count'] > 0
        })
    
    return Response(patients_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def professional_patient_summary(request, user_id):
    """Get AI-generated summary for a patient (requires consent)."""
    try:
        professional = request.user.professional_profile
        if not professional.verified:
            return Response(
                {'error': 'Only verified professionals can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
    except Professional.DoesNotExist:
        return Response(
            {'error': 'You are not a professional'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check consent
    from apps.accounts.models import User
    from apps.consent.models import ConsentGrant
    from apps.journal.models import JournalEntry
    from django.db.models import Avg, Count, Max
    from datetime import timedelta
    from django.utils import timezone
    
    patient = get_object_or_404(User, id=user_id)
    
    consent = ConsentGrant.objects.filter(
        user=patient,
        professional=professional,
        active=True
    ).first()
    
    if not consent:
        return Response(
            {'error': 'No active consent found for this patient'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get all journal entries for this patient
    entries = JournalEntry.objects.filter(user=patient).order_by('-created_at')
    
    if not entries.exists():
        return Response({
            'patientId': user_id,
            'overview': 'No journal entries available for this patient yet.',
            'keyThemes': [],
            'sentimentTrend': 'neutral',
            'averageSentiment': 0.0,
            'riskIndicators': [],
            'recommendations': ['Encourage patient to start journaling to track their mental health journey.'],
            'recentEntries': []
        })
    
    # Calculate statistics
    total_entries = entries.count()
    recent_entries = entries[:30]  # Last 30 entries for analysis
    
    # Sentiment analysis
    sentiment_scores = [e.sentiment_score for e in recent_entries if e.sentiment_score is not None]
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
    
    # Determine sentiment trend
    if len(sentiment_scores) >= 7:
        recent_7 = sentiment_scores[:7]
        older_7 = sentiment_scores[7:14] if len(sentiment_scores) >= 14 else sentiment_scores[7:]
        if older_7:
            recent_avg = sum(recent_7) / len(recent_7)
            older_avg = sum(older_7) / len(older_7)
            if recent_avg > older_avg + 0.1:
                sentiment_trend = 'improving'
            elif recent_avg < older_avg - 0.1:
                sentiment_trend = 'declining'
            else:
                sentiment_trend = 'stable'
        else:
            sentiment_trend = 'stable'
    else:
        sentiment_trend = 'stable' if avg_sentiment > 0 else 'declining' if avg_sentiment < -0.3 else 'stable'
    
    # Aggregate key themes
    all_themes = []
    for entry in recent_entries:
        if entry.key_themes:
            all_themes.extend(entry.key_themes)
    
    # Count theme frequency
    theme_counts = {}
    for theme in all_themes:
        theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    # Get top 5 themes
    key_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    key_themes_list = [theme[0] for theme in key_themes]
    
    # Risk indicators
    risk_indicators = []
    high_risk_count = 0
    for entry in recent_entries:
        if entry.risk_flags:
            if isinstance(entry.risk_flags, dict):
                for flag, value in entry.risk_flags.items():
                    if value:
                        if flag in ['suicidal_ideation', 'self_harm', 'crisis']:
                            high_risk_count += 1
                            if flag not in risk_indicators:
                                risk_indicators.append(flag.replace('_', ' ').title())
    
    if high_risk_count > 0:
        risk_indicators.insert(0, f'High-risk indicators detected ({high_risk_count} entries)')
    
    # Check for intensity issues
    high_intensity_count = sum(1 for e in recent_entries if e.intensity_score and e.intensity_score > 0.8)
    if high_intensity_count > 0:
        risk_indicators.append(f'High emotional intensity in {high_intensity_count} entries')
    
    # Check for negative sentiment patterns
    negative_count = sum(1 for e in recent_entries if e.sentiment_score and e.sentiment_score < -0.5)
    if negative_count > len(recent_entries) * 0.5:  # More than 50% negative
        risk_indicators.append('Consistent negative sentiment patterns')
    
    if not risk_indicators:
        risk_indicators = ['No significant risk indicators detected']
    
    # Generate AI-powered comprehensive overview
    try:
        from utils.ai_service import ai_service
        from apps.chat.models import ChatSession, ChatMessage

        # Prepare journal data for AI
        journals_data = []
        for entry in recent_entries:
            journals_data.append({
                'content': entry.text_encrypted,
                'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M'),
                'detected_emotions': ', '.join([e.get('emotion', '') for e in entry.detected_emotions]) if entry.detected_emotions else 'None'
            })

        # Get chat history if available
        chat_history_data = None
        chat_sessions = ChatSession.objects.filter(user=patient, status__in=['open', 'escalated', 'closed']).order_by('-created_at')
        if chat_sessions.exists():
            latest_session = chat_sessions.first()
            messages = ChatMessage.objects.filter(session=latest_session).order_by('created_at')[:50]
            chat_history_data = []
            for msg in messages:
                chat_history_data.append({
                    'role': msg.sender,
                    'content': msg.content_encrypted
                })

        # Generate AI summary
        ai_overview = ai_service.generate_patient_summary(journals_data, chat_history_data)
        overview = ai_overview

    except Exception as e:
        print(f"Warning: AI summary generation failed, using fallback: {e}")
        # Fallback to rule-based overview
        if avg_sentiment > 0.3:
            overview = f"Patient shows overall positive patterns with {total_entries} journal entries. "
            if sentiment_trend == 'improving':
                overview += "Recent entries indicate continued improvement in mood and coping mechanisms."
            else:
                overview += "Sentiment remains stable."
        elif avg_sentiment < -0.3:
            overview = f"Patient shows challenging emotional patterns across {total_entries} entries. "
            if key_themes_list:
                overview += f"Key concerns include {', '.join(key_themes_list[:3])}. "
            if sentiment_trend == 'declining':
                overview += "Recent entries show a decline in emotional well-being that requires attention."
            else:
                overview += "Monitoring and support are recommended."
        else:
            overview = f"Patient has {total_entries} journal entries showing mixed emotional states. "
            if key_themes_list:
                overview += f"Common themes include {', '.join(key_themes_list[:3])}. "
            overview += "Regular monitoring is advised."
    
    # Generate recommendations
    recommendations = []
    if avg_sentiment < -0.3:
        recommendations.append('Consider scheduling a follow-up session to discuss recent challenges')
        recommendations.append('Review coping strategies and support systems')
    if high_risk_count > 0:
        recommendations.append('Immediate attention required - high-risk indicators present')
        recommendations.append('Consider escalation or crisis intervention protocols')
    if high_intensity_count > 0:
        recommendations.append('Monitor emotional intensity levels closely')
    if sentiment_trend == 'declining':
        recommendations.append('Intervention may be needed - sentiment trend is declining')
    if not recommendations:
        recommendations.append('Continue current treatment approach')
        recommendations.append('Encourage consistent journaling to track progress')
    
    # Recent entries summary
    recent_entries_list = []
    for entry in recent_entries[:10]:  # Last 10 entries
        # Determine mood from sentiment and themes
        mood = 'neutral'
        if entry.sentiment_score:
            if entry.sentiment_score > 0.5:
                mood = 'positive, optimistic'
            elif entry.sentiment_score > 0.2:
                mood = 'calm, stable'
            elif entry.sentiment_score > -0.2:
                mood = 'neutral, reflective'
            elif entry.sentiment_score > -0.5:
                mood = 'anxious, stressed'
            else:
                mood = 'distressed, overwhelmed'
        
        # Extract risk flags
        risk_flags = []
        if entry.risk_flags:
            if isinstance(entry.risk_flags, dict):
                for flag, value in entry.risk_flags.items():
                    if value:
                        risk_flags.append(flag.replace('_', ' ').title())
        
        recent_entries_list.append({
            'date': entry.created_at.isoformat(),
            'sentiment': round(entry.sentiment_score, 2) if entry.sentiment_score else 0.0,
            'summary': entry.ai_summary or 'No summary available',
            'themes': entry.key_themes[:3] if entry.key_themes else [],
            'mood': mood,
            'riskFlags': risk_flags
        })
    
    return Response({
        'patientId': user_id,
        'overview': overview,
        'keyThemes': key_themes_list,
        'sentimentTrend': sentiment_trend,
        'averageSentiment': round(avg_sentiment, 2),
        'riskIndicators': risk_indicators,
        'recommendations': recommendations,
        'recentEntries': recent_entries_list,
        'totalEntries': total_entries,
        'entriesAnalyzed': len(recent_entries)
    })
