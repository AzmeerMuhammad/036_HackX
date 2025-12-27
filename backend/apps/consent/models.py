from django.db import models
from apps.accounts.models import User
from apps.professionals.models import Professional


class ConsentGrant(models.Model):
    """
    Consent to share patient history with a professional.
    Once granted, the professional can view the user's journal history.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='consent_grants',
        help_text="User granting consent"
    )
    professional = models.ForeignKey(
        Professional, 
        on_delete=models.CASCADE, 
        related_name='consent_grants',
        help_text="Professional receiving consent"
    )
    active = models.BooleanField(
        default=True,
        help_text="Is this consent currently active? (Cannot be revoked in MVP)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consent_consentgrant'
        verbose_name = 'Consent Grant'
        verbose_name_plural = 'Consent Grants'
        unique_together = ['user', 'professional']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'active']),
            models.Index(fields=['professional', 'active']),
        ]

    def __str__(self):
        return f"{self.user.display_name} -> {self.professional.user.display_name}"

