from django.contrib import admin
from .models import Tag, DataSchema, DataField, Dataset, DatasetFile, DatasetProfile


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']


class DataFieldInline(admin.TabularInline):
    model = DataField
    extra = 1


@admin.register(DataSchema)
class DataSchemaAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['version']
    filter_horizontal = ['tags']
    inlines = [DataFieldInline]


@admin.register(DataField)
class DataFieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'schema', 'field_type', 'required']
    list_filter = ['field_type', 'required']
    search_fields = ['name', 'description']


class DatasetFileInline(admin.TabularInline):
    model = DatasetFile
    extra = 1


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'schema', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['schema']
    filter_horizontal = ['tags']
    inlines = [DatasetFileInline]


@admin.register(DatasetFile)
class DatasetFileAdmin(admin.ModelAdmin):
    list_display = ['file_path', 'dataset', 'file_size', 'file_format', 'uploaded_at']
    list_filter = ['file_format']
    search_fields = ['file_path']


@admin.register(DatasetProfile)
class DatasetProfileAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'row_count', 'column_count', 'created_at']
    search_fields = ['dataset__name']

