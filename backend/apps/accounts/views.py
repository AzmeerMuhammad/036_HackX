from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserSerializer
from .models import User


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Log validation errors for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Registration validation errors: {serializer.errors}')
            # Return detailed validation errors
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = serializer.save()
            
            # Create Professional record if user is a professional
            # (Backup in case signal doesn't fire)
            if user.is_professional:
                try:
                    from apps.professionals.models import Professional
                    Professional.objects.get_or_create(
                        user=user,
                        defaults={
                            'specialization': user.professional_type or 'General Practice',
                            'availability': '',
                            'city': '',
                            'verified': False
                        }
                    )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f'Could not create Professional record: {str(e)}')
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Registration error: {str(e)}', exc_info=True)
            return Response(
                {'error': f'Registration failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """User login endpoint."""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    """Get or update current user info."""
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)

    elif request.method == 'PATCH':
        # Allow updating specific fields
        user = request.user

        # Update display_name if provided
        if 'display_name' in request.data:
            user.display_name = request.data['display_name']

        user.save()
        return Response(UserSerializer(user).data)

