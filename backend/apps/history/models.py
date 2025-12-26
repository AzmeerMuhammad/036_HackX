from django.db import models
from apps.accounts.models import User


class PatientHistorySnapshot(models.Model):
    """Patient history snapshot stored as JSON."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_snapshots')
    json_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"History Snapshot - {self.user.display_name} - {self.created_at.date()}"

