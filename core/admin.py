from django.contrib import admin
from .models import Tag, DataSchema, DataField, Dataset, DatasetFile, DatasetProfile, AuditLog


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'category', 'version', 'is_active', 'created_at', 'updated_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['created_at', 'updated_at']


class DataFieldInline(admin.TabularInline):
    model = DataField
    extra = 1
    fields = ['name', 'display_name', 'data_type', 'is_required', 'allow_null', 'order']


@admin.register(DataSchema)
class DataSchemaAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'version', 'is_default', 'is_active', 'created_at']
    list_filter = ['tag', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DataFieldInline]


@admin.register(DataField)
class DataFieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'data_schema', 'data_type', 'is_required', 'allow_null', 'order']
    list_filter = ['data_type', 'is_required', 'allow_null']
    search_fields = ['name', 'display_name', 'description']


class DatasetFileInline(admin.TabularInline):
    model = DatasetFile
    extra = 1
    readonly_fields = ['uploaded_at', 'filesize', 'checksum']


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'data_schema', 'status', 'source_type', 'num_records', 'created_at']
    list_filter = ['status', 'source_type', 'tag']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'ingested_at', 'num_records']
    inlines = [DatasetFileInline]


@admin.register(DatasetFile)
class DatasetFileAdmin(admin.ModelAdmin):
    list_display = ['file_path', 'dataset', 'file_format', 'filesize', 'uploaded_at', 'order']
    list_filter = ['file_format']
    search_fields = ['file_path', 'dataset__name']
    readonly_fields = ['uploaded_at', 'filesize', 'checksum']


@admin.register(DatasetProfile)
class DatasetProfileAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'generated_at']
    search_fields = ['dataset__name']
    readonly_fields = ['generated_at', 'profile_json']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'target_type', 'target_id', 'user', 'created_at']
    list_filter = ['event_type', 'target_type']
    search_fields = ['message', 'target_id']
    readonly_fields = ['event_type', 'user', 'target_type', 'target_id', 'message', 'payload', 'created_at']


