from django.db import models
from django.conf import settings
from core.models import Tag, DataSchema, Dataset


class AnalysisTemplate(models.Model):
    """Template for analysis operations."""
    name = models.CharField(max_length=200)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='analysis_templates')
    data_schema = models.ForeignKey(
        DataSchema,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analysis_templates'
    )
    description = models.TextField(blank=True)
    parameters_schema = models.TextField(
        blank=True,
        help_text="JSON Schema formatted parameter definition"
    )
    code_identifier = models.CharField(
        max_length=200,
        blank=True,
        help_text="Python module/function identifier (e.g., 'analysis.pipeline.basic_stats')"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AnalysisRun(models.Model):
    """Execution of an analysis template."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    template = models.ForeignKey(AnalysisTemplate, on_delete=models.CASCADE, related_name='runs')
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analysis_runs'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    parameters = models.TextField(blank=True, help_text="JSON formatted parameters")
    result_path = models.CharField(max_length=500, blank=True, null=True)
    result_summary = models.TextField(blank=True, null=True, help_text="JSON formatted result summary")
    log = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analysis_runs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.template.name} - {self.status}"


