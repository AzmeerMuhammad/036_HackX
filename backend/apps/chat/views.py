from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer, ChatMessageCreateSerializer
from .services import generate_bot_response, create_escalation_ticket


class ChatSessionListCreateView(generics.ListCreateAPIView):
    """List user's chat sessions or create a new one."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatSessionSerializer
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Get most recent open session or create new one
        session = ChatSession.objects.filter(
            user=request.user,
            status='open'
        ).order_by('-created_at').first()

        if session:
            # Return existing session
            serializer = self.get_serializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create new session
            session = ChatSession.objects.create(
                user=request.user,
                status='open',
                is_anonymous=False
            )
            serializer = self.get_serializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request, session_id):
    """Send a message in a chat session and get bot response."""
    session = get_object_or_404(
        ChatSession,
        id=session_id,
        user=request.user
    )
    
    if session.status == 'closed':
        return Response(
            {'error': 'This session is closed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = ChatMessageCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_message_content = serializer.validated_data['content']
    
    # Save user message
    user_message = ChatMessage.objects.create(
        session=session,
        sender='user',
        content_encrypted=user_message_content
    )
    
    # Get conversation history
    conversation_history = list(session.messages.all())
    
    # Generate bot response
    bot_response_data = generate_bot_response(
        user_message_content,
        session,
        conversation_history
    )
    
    # Save bot message
    bot_message = ChatMessage.objects.create(
        session=session,
        sender='bot',
        content_encrypted=bot_response_data['content']
    )
    
    # Escalate if needed
    escalation_ticket = None
    if bot_response_data['escalate']:
        reason = f"Dangerous level detected in chat message: {user_message_content[:100]}"
        escalation_ticket = create_escalation_ticket(session, reason)
    
    return Response({
        'user_message': ChatMessageSerializer(user_message).data,
        'bot_message': ChatMessageSerializer(bot_message).data,
        'escalated': bot_response_data['escalate'],
        'escalation_ticket_id': escalation_ticket.id if escalation_ticket else None,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_messages(request, session_id):
    """Get all messages in a chat session."""
    session = get_object_or_404(
        ChatSession,
        id=session_id,
        user=request.user
    )
    
    messages = session.messages.all()
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_session(request, session_id):
    """Update chat session (e.g., toggle anonymous mode)."""
    session = get_object_or_404(
        ChatSession,
        id=session_id,
        user=request.user
    )
    
    if 'is_anonymous' in request.data:
        session.is_anonymous = request.data['is_anonymous']
        session.save(update_fields=['is_anonymous'])
    
    serializer = ChatSessionSerializer(session)
    return Response(serializer.data)

