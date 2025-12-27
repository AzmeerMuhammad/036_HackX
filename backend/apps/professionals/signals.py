"""
Signals to automatically create Professional records when users register as professionals.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save)
def create_professional_profile(sender, **kwargs):
    """
    Automatically create Professional record when a user registers with is_professional=True.
    """
    # Only process User model saves
    from apps.accounts.models import User
    if sender != User:
        return
    
    instance = kwargs.get('instance')
    created = kwargs.get('created')
    
    if created and hasattr(instance, 'is_professional') and instance.is_professional:
        try:
            # Import here to avoid circular imports
            from apps.professionals.models import Professional
            # Only create if it doesn't exist
            professional, was_created = Professional.objects.get_or_create(
                user=instance,
                defaults={
                    'specialization': getattr(instance, 'professional_type', None) or 'General Practice',
                    'availability': '',
                    'city': '',
                    'verified': False  # Will be auto-verified when profile is complete
                }
            )
            if was_created:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f'Created Professional record for {instance.username}')
        except Exception as e:
            # Log error but don't break registration
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error creating professional record for {instance.username}: {str(e)}', exc_info=True)

