from django.db import models
from apps.accounts.models import User


class Professional(models.Model):
    """
    Professional (psychiatrist/doctor) profile.
    Extends User model with professional-specific information.
    """
    PROFESSIONAL_TYPE_CHOICES = [
        ('psychiatrist', 'Psychiatrist'),
        ('therapist', 'Therapist'),
        ('psychologist', 'Psychologist'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='professional_profile',
        help_text="User account linked to this professional profile"
    )
    professional_type = models.CharField(
        max_length=50,
        choices=PROFESSIONAL_TYPE_CHOICES,
        blank=True,
        default='',
        help_text="Type of professional (psychiatrist, therapist, psychologist)"
    )
    specialization = models.CharField(max_length=200, blank=True, default='', help_text="Area of specialization (e.g., Anxiety, Depression)")
    availability = models.TextField(blank=True, help_text="Professional availability schedule")
    verified = models.BooleanField(default=False, help_text="Has this professional been verified?")
    city = models.CharField(max_length=100, blank=True, default='', help_text="City where professional practices")

    # Verification fields
    pmdc_id = models.CharField(max_length=100, blank=True, default='', help_text="PMDC ID for psychiatrists")
    degree_picture = models.ImageField(upload_to='professional_degrees/', blank=True, null=True, help_text="Degree certificate for therapists/psychologists")
    university_name = models.CharField(max_length=200, blank=True, default='', help_text="University name for therapists/psychologists")

    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """Auto-verify professional when profile is complete."""
        # Check if verification requirements are met
        if self.has_verification_documents() and not self.verified:
            self.verified = True

        super().save(*args, **kwargs)

    def has_verification_documents(self):
        """Check if professional has submitted required verification documents."""
        if not self.professional_type:
            return False

        if self.professional_type == 'psychiatrist':
            return bool(self.pmdc_id and self.pmdc_id.strip())
        else:  # therapist or psychologist
            return bool(
                self.degree_picture and
                self.university_name and
                self.university_name.strip()
            )


    class Meta:
        db_table = 'professionals_professional'
        verbose_name = 'Professional'
        verbose_name_plural = 'Professionals'
        ordering = ['-created_at']

    def is_profile_complete(self):
        """Check if professional profile has all required fields."""
        # Both specialization and city must be filled
        has_specialization = self.specialization and self.specialization.strip()
        has_city = self.city and self.city.strip()
        return has_specialization and has_city
    
    def get_missing_fields(self):
        """Get list of missing required fields."""
        missing = []
        if not self.specialization or not self.specialization.strip():
            missing.append('specialization')
        if not self.city or not self.city.strip():
            missing.append('city')
        return missing
    
    def get_profile_completion_percentage(self):
        """Get profile completion percentage."""
        fields = {
            'specialization': self.specialization,
            'city': self.city,
            'availability': self.availability,
        }
        completed = sum(1 for field in fields.values() if field and field.strip())
        return int((completed / len(fields)) * 100)
    
    def __str__(self):
        return f"{self.user.display_name} - {self.specialization}"


class ProfessionalSOPDoc(models.Model):
    """
    SOP (Standard Operating Procedure) documents created by professionals 
    for chatbot guidance and responses.
    """
    title = models.CharField(max_length=200, help_text="Title of the SOP document")
    category = models.CharField(
        max_length=100, 
        help_text="Category (e.g., anxiety, depression, self-harm-risk, panic)"
    )
    content = models.TextField(help_text="SOP content/guidelines")
    created_by_professional = models.ForeignKey(
        Professional, 
        on_delete=models.CASCADE, 
        related_name='sop_docs',
        help_text="Professional who created this SOP"
    )
    active = models.BooleanField(default=True, help_text="Is this SOP currently active?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'professionals_professionalsopdoc'
        verbose_name = 'Professional SOP Document'
        verbose_name_plural = 'Professional SOP Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'active']),
        ]

    def __str__(self):
        return f"{self.title} ({self.category})"


class EscalationTicket(models.Model):
    """
    Escalation ticket for professional review.
    Created when chatbot detects high-risk situations or user requests escalation.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
    ]
    
    VERDICT_CHOICES = [
        ('consult_required', 'Consult Required'),
        ('monitor', 'Monitor'),
        ('no_action', 'No Action'),
    ]
    
    session = models.ForeignKey(
        'chat.ChatSession', 
        on_delete=models.CASCADE, 
        related_name='escalation_tickets',
        help_text="Chat session that triggered this escalation"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='escalation_tickets',
        help_text="User who needs professional review"
    )
    assigned_professional = models.ForeignKey(
        Professional, 
        on_delete=models.CASCADE, 
        related_name='assigned_tickets',
        help_text="Professional assigned to review this ticket"
    )
    reason = models.TextField(help_text="Reason for escalation")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES, blank=True, null=True)
    professional_notes = models.TextField(blank=True, help_text="Notes from the reviewing professional")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True, help_text="When was this ticket reviewed?")

    class Meta:
        db_table = 'professionals_escalationticket'
        verbose_name = 'Escalation Ticket'
        verbose_name_plural = 'Escalation Tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['assigned_professional', 'status']),
        ]

    def __str__(self):
        return f"Ticket #{self.id} - {self.user.display_name}"

