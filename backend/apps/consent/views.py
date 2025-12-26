from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ConsentGrant
from .serializers import ConsentGrantSerializer, ConsentGrantCreateSerializer
from apps.professionals.models import Professional


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grant_consent(request):
    """Grant consent to share history with a professional."""
    serializer = ConsentGrantCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    professional = get_object_or_404(
        Professional,
        id=serializer.validated_data['professional_id'],
        verified=True
    )
    
    consent, created = ConsentGrant.objects.get_or_create(
        user=request.user,
        professional=professional,
        defaults={'active': True}
    )
    
    if not created:
        consent.active = True
        consent.save()
    
    return Response(
        ConsentGrantSerializer(consent).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consent_status(request):
    """Get user's consent grants."""
    consents = ConsentGrant.objects.filter(user=request.user, active=True)
    serializer = ConsentGrantSerializer(consents, many=True)
    return Response(serializer.data)

