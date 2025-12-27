"""
Management command to sync users with is_professional=True to Professional records.
This creates Professional records for users who have is_professional=True but no Professional record.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.professionals.models import Professional


class Command(BaseCommand):
    help = 'Sync users with is_professional=True to Professional records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Also verify the professionals after creating them',
        )
        parser.add_argument(
            '--verify-all',
            action='store_true',
            help='Verify all existing professionals',
        )

    def handle(self, *args, **options):
        self.stdout.write('Syncing professionals...')
        
        # Find all users with is_professional=True
        professional_users = User.objects.filter(is_professional=True)
        
        created_count = 0
        updated_count = 0
        
        for user in professional_users:
            professional, created = Professional.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': user.professional_type or 'General Practice',
                    'availability': '',
                    'city': '',
                    'verified': options['verify'] or False
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created Professional record for: {user.display_name or user.username}'
                    )
                )
            else:
                # Update existing professional if verify flag is set
                if options['verify'] and not professional.verified:
                    professional.verified = True
                    professional.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Verified Professional: {user.display_name or user.username}'
                        )
                    )
        
        # Verify all professionals if requested
        if options['verify_all']:
            verified = Professional.objects.filter(verified=False).update(verified=True)
            self.stdout.write(
                self.style.SUCCESS(f'Verified {verified} existing professionals')
            )
        
        # Show summary
        total_professionals = Professional.objects.count()
        verified_professionals = Professional.objects.filter(verified=True).count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  Created: {created_count} new Professional records')
        self.stdout.write(f'  Updated: {updated_count} existing records')
        self.stdout.write(f'  Total Professionals: {total_professionals}')
        self.stdout.write(f'  Verified Professionals: {verified_professionals}')
        self.stdout.write('='*50)

