from django.contrib import admin
from .models import Professional, ProfessionalSOPDoc, EscalationTicket


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'verified', 'city', 'created_at')
    list_filter = ('verified', 'city')
    search_fields = ('user__username', 'specialization', 'city')


@admin.register(ProfessionalSOPDoc)
class ProfessionalSOPDocAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by_professional', 'active', 'created_at')
    list_filter = ('category', 'active')


@admin.register(EscalationTicket)
class EscalationTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'assigned_professional', 'status', 'verdict', 'created_at')
    list_filter = ('status', 'verdict')

