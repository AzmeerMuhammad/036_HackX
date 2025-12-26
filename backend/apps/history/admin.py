from django.contrib import admin
from .models import PatientHistorySnapshot


@admin.register(PatientHistorySnapshot)
class PatientHistorySnapshotAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('json_data',)

