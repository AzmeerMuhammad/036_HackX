from django.db import models
from apps.accounts.models import User


class Professional(models.Model):
    """Professional (psychiatrist/doctor) profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional_profile')
    specialization = models.CharField(max_length=200)
    availability = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.display_name} - {self.specialization}"


class ProfessionalSOPDoc(models.Model):
    """SOP documents created by professionals for chatbot guidance."""
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)  # e.g., anxiety, depression, self-harm-risk, panic
    content = models.TextField()
    created_by_professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='sop_docs')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.category})"


class EscalationTicket(models.Model):
    """Escalation ticket for professional review."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
    ]
    
    VERDICT_CHOICES = [
        ('consult_required', 'Consult Required'),
        ('monitor', 'Monitor'),
        ('no_action', 'No Action'),
    ]
    
    session = models.ForeignKey('chat.ChatSession', on_delete=models.CASCADE, related_name='escalation_tickets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escalation_tickets')
    assigned_professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='assigned_tickets')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES, blank=True, null=True)
    professional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.user.display_name}"

