from django.urls import path
from .views import generate_history, get_pdf, professional_patient_history

urlpatterns = [
    path('generate/', generate_history, name='history-generate'),
    path('pdf/<int:snapshot_id>/', get_pdf, name='history-pdf'),
    path('professional/patients/<int:user_id>/history/latest/', professional_patient_history, name='professional-patient-history'),
]

