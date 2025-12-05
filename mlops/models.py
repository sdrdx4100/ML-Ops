from django.db import models
from core.models import Tag, Dataset


class MLModel(models.Model):
    """Machine learning model definition."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    model_type = models.CharField(max_length=100, blank=True)
    framework = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='ml_models')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MLModelVersion(models.Model):
    """Version of an ML model."""
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=50)
    artifact_path = models.CharField(max_length=500, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['model', 'version']

    def __str__(self):
        return f"{self.model.name} v{self.version}"


class MLTrainingRun(models.Model):
    """Training run for an ML model."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='training_runs')
    model_version = models.ForeignKey(MLModelVersion, on_delete=models.SET_NULL, null=True, blank=True, related_name='training_runs')
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, blank=True, related_name='training_runs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hyperparameters = models.JSONField(default=dict, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model.name} training - {self.status}"

