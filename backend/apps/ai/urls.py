from django.urls import path
from .views import analyze_journal_view

urlpatterns = [
    path('analyze-journal/', analyze_journal_view, name='analyze-journal'),
]

