from django.db import models
from apps.accounts.models import User


class PatientHistorySnapshot(models.Model):
    """
    Patient history snapshot stored as JSON.
    Contains 7-day journal summaries, themes, risk trends, and chat highlights.
    Used for generating PDF reports to share with professionals.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='history_snapshots',
        help_text="User whose history is being snapshotted"
    )
    json_data = models.JSONField(help_text="Complete history data in JSON format")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'history_patienthistorysnapshot'
        verbose_name = 'Patient History Snapshot'
        verbose_name_plural = 'Patient History Snapshots'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"History Snapshot - {self.user.display_name} - {self.created_at.date()}"

