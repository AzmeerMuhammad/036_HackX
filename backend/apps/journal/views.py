from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import JournalEntry
from .serializers import JournalEntrySerializer, JournalEntryCreateSerializer


class JournalEntryListCreateView(generics.ListCreateAPIView):
    """List user's journal entries or create a new one."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JournalEntryCreateSerializer
        return JournalEntrySerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        entry = serializer.save()
        return Response(
            JournalEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED
        )


class JournalEntryDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a journal entry."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JournalEntrySerializer
    
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)

