from django.db import models


class Job(models.Model):
    """Generic job for asynchronous task execution."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    job_type = models.CharField(
        max_length=100,
        help_text="Type of job: analysis_run, ml_training"
    )
    target_id = models.CharField(
        max_length=100,
        help_text="ID of the target object (AnalysisRun.id or MLTrainingRun.id)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(default=0)
    queue = models.CharField(max_length=100, default='default')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    log = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'created_at']

    def __str__(self):
        return f"{self.job_type}:{self.target_id} ({self.status})"


