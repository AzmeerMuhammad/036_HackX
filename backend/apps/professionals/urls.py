from django.urls import path
from .views import (
    ProfessionalListView, ProfessionalApplyView,
    my_escalations, professional_escalations,
    professional_escalation_detail, professional_escalation_verdict,
    professional_patients, professional_profile, professional_patient_summary
)

urlpatterns = [
    path('list/', ProfessionalListView.as_view(), name='professional-list'),
    path('apply/', ProfessionalApplyView.as_view(), name='professional-apply'),
    path('profile/', professional_profile, name='professional-profile'),
    path('patients/', professional_patients, name='professional-patients'),
    path('patients/<int:user_id>/summary/', professional_patient_summary, name='professional-patient-summary'),
    path('escalations/', professional_escalations, name='professional-escalations'),
    path('escalations/<int:ticket_id>/', professional_escalation_detail, name='professional-escalation-detail'),
    path('escalations/<int:ticket_id>/verdict/', professional_escalation_verdict, name='professional-escalation-verdict'),
]

# Escalations endpoints (user-facing)
urlpatterns += [
    path('escalations/mine/', my_escalations, name='my-escalations'),
]

