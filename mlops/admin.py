from django.contrib import admin
from .models import MLModel, MLModelVersion, MLTrainingRun


class MLModelVersionInline(admin.TabularInline):
    model = MLModelVersion
    extra = 1
    readonly_fields = ['created_at', 'updated_at', 'artifact_path', 'metrics']


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'task_type', 'is_active', 'created_at', 'updated_at']
    list_filter = ['tag', 'task_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MLModelVersionInline]


@admin.register(MLModelVersion)
class MLModelVersionAdmin(admin.ModelAdmin):
    list_display = ['model', 'version', 'status', 'trained_on_dataset', 'created_at']
    list_filter = ['status', 'model']
    search_fields = ['model__name', 'version']
    readonly_fields = ['created_at', 'updated_at', 'artifact_path', 'metrics']


@admin.register(MLTrainingRun)
class MLTrainingRunAdmin(admin.ModelAdmin):
    list_display = ['model_version', 'status', 'started_at', 'finished_at', 'created_at']
    list_filter = ['status', 'model_version__model']
    search_fields = ['model_version__model__name', 'model_version__version']
    readonly_fields = ['created_at', 'started_at', 'finished_at', 'log']

