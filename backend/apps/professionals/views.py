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
    queryset = Professional.objects.filter(verified=True)
    permission_classes = [permissions.AllowAny]
    serializer_class = ProfessionalSerializer


class ProfessionalApplyView(generics.CreateAPIView):
    """Apply to become a professional."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfessionalApplySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        professional = serializer.save()
        return Response(
            ProfessionalSerializer(professional).data,
            status=status.HTTP_201_CREATED
        )


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

