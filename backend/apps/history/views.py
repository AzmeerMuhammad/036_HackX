from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import PatientHistorySnapshot
from .services import generate_history_json
from .pdf_generator import generate_pdf
from apps.consent.models import ConsentGrant
from apps.professionals.models import Professional


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_history(request):
    """Generate patient history snapshot."""
    try:
        history_json = generate_history_json(request.user)
        
        snapshot = PatientHistorySnapshot.objects.create(
            user=request.user,
            json_data=history_json
        )
        
        return Response({
            'snapshot_id': snapshot.id,
            'generated_at': snapshot.created_at.isoformat(),
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generating history snapshot: {error_details}")  # Log for debugging
        return Response(
            {'error': f'Failed to generate history snapshot: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pdf(request, snapshot_id):
    """Get history snapshot as branded PDF."""
    snapshot = get_object_or_404(
        PatientHistorySnapshot,
        id=snapshot_id,
        user=request.user
    )
    
    pdf_buffer = generate_pdf(snapshot.json_data)
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="patient_history_{snapshot_id}.pdf"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def professional_patient_history(request, user_id):
    """Get patient history for a professional (requires consent)."""
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
    
    # Get latest snapshot or generate new one
    snapshot = PatientHistorySnapshot.objects.filter(user=patient).first()
    if not snapshot:
        history_json = generate_history_json(patient)
        snapshot = PatientHistorySnapshot.objects.create(
            user=patient,
            json_data=history_json
        )
    
    return Response({
        'snapshot_id': snapshot.id,
        'json_data': snapshot.json_data,
        'generated_at': snapshot.created_at.isoformat(),
    })

