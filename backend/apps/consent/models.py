from django.db import models
from apps.accounts.models import User
from apps.professionals.models import Professional


class ConsentGrant(models.Model):
    """Consent to share patient history with a professional."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consent_grants')
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='consent_grants')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'professional']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.display_name} -> {self.professional.user.display_name}"

