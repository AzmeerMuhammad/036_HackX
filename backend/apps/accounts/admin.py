from django.contrib import admin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'display_name', 'email', 'is_professional', 'has_professional_record', 'is_staff', 'created_at')
    list_filter = ('is_professional', 'is_staff', 'professional_type')
    search_fields = ('username', 'email', 'display_name')
    actions = ['create_professional_records', 'verify_professionals']
    
    def has_professional_record(self, obj):
        """Check if user has a Professional record"""
        try:
            has_record = hasattr(obj, 'professional_profile')
            if has_record:
                prof = obj.professional_profile
                status = '✓ Verified' if prof.verified else '✗ Not Verified'
                color = 'green' if prof.verified else 'orange'
                return format_html('<span style="color: {};">{}</span>', color, status)
            return format_html('<span style="color: red;">No Record</span>')
        except:
            return format_html('<span style="color: red;">No Record</span>')
    has_professional_record.short_description = 'Professional Status'
    
    def create_professional_records(self, request, queryset):
        """Create Professional records for selected users who have is_professional=True"""
        from apps.professionals.models import Professional
        
        created_count = 0
        skipped_count = 0
        
        for user in queryset:
            if not user.is_professional:
                skipped_count += 1
                continue
            
            professional, created = Professional.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': user.professional_type or 'General Practice',
                    'availability': '',
                    'city': '',
                    'verified': False
                }
            )
            
            if created:
                created_count += 1
                self.message_user(
                    request,
                    f'Created Professional record for {user.username}',
                    level='success'
                )
            else:
                skipped_count += 1
        
        self.message_user(
            request,
            f'Created {created_count} Professional record(s). Skipped {skipped_count} user(s).',
            level='success'
        )
    create_professional_records.short_description = 'Create Professional records for selected users'
    
    def verify_professionals(self, request, queryset):
        """Verify Professional records for selected users"""
        from apps.professionals.models import Professional
        
        verified_count = 0
        
        for user in queryset:
            if not user.is_professional:
                continue
            
            try:
                professional = user.professional_profile
                if not professional.verified:
                    professional.verified = True
                    professional.save()
                    verified_count += 1
            except Professional.DoesNotExist:
                # Create if doesn't exist
                Professional.objects.create(
                    user=user,
                    specialization=user.professional_type or 'General Practice',
                    verified=True
                )
                verified_count += 1
        
        self.message_user(
            request,
            f'Verified {verified_count} professional(s).',
            level='success'
        )
    verify_professionals.short_description = 'Verify professionals for selected users'

