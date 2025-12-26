from django.urls import path
from .views import grant_consent, consent_status

urlpatterns = [
    path('grant/', grant_consent, name='consent-grant'),
    path('status/', consent_status, name='consent-status'),
]

