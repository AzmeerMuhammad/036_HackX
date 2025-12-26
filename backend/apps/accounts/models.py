from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with anonymous mode support."""
    email = models.EmailField(blank=True, null=True)
    display_name = models.CharField(max_length=100, blank=True)
    is_anonymous_mode = models.BooleanField(default=True)
    is_professional = models.BooleanField(default=False)
    professional_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('psychiatrist', 'Psychiatrist'),
            ('therapist', 'Therapist'),
            ('psychologist', 'Psychologist'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.username


class UserProfile(models.Model):
    """Extended user profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.display_name}'s Profile"

