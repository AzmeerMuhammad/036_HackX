from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with anonymous mode support.
    All user information is stored directly in this model for simplicity.
    """
    email = models.EmailField(blank=True, null=True)
    display_name = models.CharField(max_length=100, blank=True, help_text="Display name shown to others")
    is_anonymous_mode = models.BooleanField(default=True, help_text="User prefers anonymous mode")
    is_professional = models.BooleanField(default=False, help_text="Is this user a mental health professional?")
    professional_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('psychiatrist', 'Psychiatrist'),
            ('therapist', 'Therapist'),
            ('psychologist', 'Psychologist'),
        ],
        help_text="Type of professional (only if is_professional=True)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.display_name or self.username

