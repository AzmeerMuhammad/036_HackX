from django.urls import path
from .views import ChatSessionListCreateView, send_message, get_messages

urlpatterns = [
    path('sessions/', ChatSessionListCreateView.as_view(), name='chat-sessions'),
    path('sessions/<int:session_id>/message/', send_message, name='chat-send-message'),
    path('sessions/<int:session_id>/messages/', get_messages, name='chat-messages'),
]

