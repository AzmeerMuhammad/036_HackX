from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from .services import analyze_journal


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_journal_view(request):
    """Analyze journal text and return AI insights."""
    text = request.data.get('text', '')
    if not text:
        return Response({'error': 'Text is required'}, status=400)
    
    # Get last 7 days entries for trend analysis
    from apps.journal.models import JournalEntry
    from datetime import timedelta
    from django.utils import timezone
    
    last_7_days = JournalEntry.objects.filter(
        user=request.user,
        created_at__gte=timezone.now() - timedelta(days=7)
    )
    
    analysis = analyze_journal(text, list(last_7_days))
    return Response(analysis)

