from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'job_type', 'target_id', 'status', 'priority', 'queue', 'started_at', 'finished_at']
    list_filter = ['status', 'job_type', 'queue', 'priority']
    search_fields = ['job_type', 'target_id']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'finished_at', 'log']

