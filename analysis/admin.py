from django.contrib import admin
from .models import AnalysisTemplate, AnalysisRun


@admin.register(AnalysisTemplate)
class AnalysisTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'data_schema', 'is_active', 'created_at', 'updated_at']
    list_filter = ['tag', 'is_active']
    search_fields = ['name', 'description', 'code_identifier']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'template', 'dataset', 'status', 'started_at', 'finished_at', 'created_at']
    list_filter = ['status', 'template', 'dataset']
    search_fields = ['template__name', 'dataset__name']
    readonly_fields = ['created_at', 'started_at', 'finished_at', 'result_path', 'result_summary', 'log']

