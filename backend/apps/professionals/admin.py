from django.contrib import admin
from django.utils.html import format_html
from .models import Professional, ProfessionalSOPDoc, EscalationTicket


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'verified', 'city', 'created_at', 'verify_action')
    list_filter = ('verified', 'city')
    search_fields = ('user__username', 'specialization', 'city')
    actions = ['verify_professionals', 'unverify_professionals']
    
    def verify_action(self, obj):
        if obj.verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        else:
            return format_html('<span style="color: red;">✗ Not Verified</span>')
    verify_action.short_description = 'Status'
    
    def verify_professionals(self, request, queryset):
        updated = queryset.update(verified=True)
        self.message_user(request, f'{updated} professional(s) verified successfully.')
    verify_professionals.short_description = 'Verify selected professionals'
    
    def unverify_professionals(self, request, queryset):
        updated = queryset.update(verified=False)
        self.message_user(request, f'{updated} professional(s) unverified.')
    unverify_professionals.short_description = 'Unverify selected professionals'


@admin.register(ProfessionalSOPDoc)
class ProfessionalSOPDocAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by_professional', 'active', 'created_at')
    list_filter = ('category', 'active')


@admin.register(EscalationTicket)
class EscalationTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'assigned_professional', 'status', 'verdict', 'created_at')
    list_filter = ('status', 'verdict')

