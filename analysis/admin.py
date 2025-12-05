from django.contrib import admin
from .models import AnalysisTemplate, AnalysisRun


@admin.register(AnalysisTemplate)
class AnalysisTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['template_type']
    filter_horizontal = ['tags']


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = ['template', 'dataset', 'status', 'started_at', 'completed_at', 'created_at']
    list_filter = ['status', 'template']
    search_fields = ['template__name', 'dataset__name']

