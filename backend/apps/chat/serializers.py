from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('id', 'sender', 'content_encrypted', 'created_at')
        read_only_fields = ('id', 'created_at')


class ChatMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField()


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ('id', 'status', 'created_at', 'updated_at', 'messages')
        read_only_fields = ('id', 'created_at', 'updated_at')

