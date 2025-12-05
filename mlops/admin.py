from django.contrib import admin
from .models import MLModel, MLModelVersion, MLTrainingRun


class MLModelVersionInline(admin.TabularInline):
    model = MLModelVersion
    extra = 1


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'framework', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['model_type', 'framework']
    filter_horizontal = ['tags']
    inlines = [MLModelVersionInline]


@admin.register(MLModelVersion)
class MLModelVersionAdmin(admin.ModelAdmin):
    list_display = ['model', 'version', 'is_active', 'created_at']
    list_filter = ['is_active', 'model']
    search_fields = ['model__name', 'version']


@admin.register(MLTrainingRun)
class MLTrainingRunAdmin(admin.ModelAdmin):
    list_display = ['model', 'model_version', 'dataset', 'status', 'started_at', 'completed_at']
    list_filter = ['status', 'model']
    search_fields = ['model__name']

