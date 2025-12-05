from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['name', 'job_type', 'status', 'priority', 'scheduled_at', 'started_at', 'completed_at']
    list_filter = ['status', 'job_type', 'priority']
    search_fields = ['name', 'job_type']
    readonly_fields = ['created_at', 'updated_at']

