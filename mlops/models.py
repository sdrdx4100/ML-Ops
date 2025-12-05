from django.db import models
from django.conf import settings
from core.models import Tag, DataSchema, Dataset


class MLModel(models.Model):
    """Machine learning model definition."""
    TASK_TYPE_CHOICES = [
        ('regression', 'Regression'),
        ('classification', 'Classification'),
        ('clustering', 'Clustering'),
    ]

    name = models.CharField(max_length=200)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='ml_models')
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, default='regression')
    input_schema = models.ForeignKey(
        DataSchema,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_input_models'
    )
    output_schema = models.ForeignKey(
        DataSchema,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_output_models'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MLModelVersion(models.Model):
    """Version of an ML model."""
    STATUS_CHOICES = [
        ('training', 'Training'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
        ('deprecated', 'Deprecated'),
    ]

    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='training')
    artifact_path = models.CharField(max_length=500, blank=True)
    metrics = models.TextField(blank=True, help_text="JSON formatted metrics")
    trained_on_dataset = models.ForeignKey(
        Dataset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trained_model_versions'
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['model', 'version']

    def __str__(self):
        return f"{self.model.name} v{self.version}"


class MLTrainingRun(models.Model):
    """Training run for an ML model."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    model_version = models.ForeignKey(
        MLModelVersion,
        on_delete=models.CASCADE,
        related_name='training_runs'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hyperparams = models.TextField(blank=True, help_text="JSON formatted hyperparameters")
    log = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_runs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model_version.model.name} v{self.model_version.version} training - {self.status}"


