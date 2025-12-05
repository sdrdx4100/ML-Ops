from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """Abstract base model with common audit fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )

    class Meta:
        abstract = True


class Tag(BaseModel):
    """Tag for categorizing and organizing data."""
    CATEGORY_CHOICES = [
        ('dataset', 'Dataset'),
        ('analysis', 'Analysis'),
        ('ml_task', 'ML Task'),
    ]

    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='dataset')
    version = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class DataSchema(BaseModel):
    """Schema definition for datasets."""
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='schemas')
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50, default='1.0')
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    extra_meta = models.TextField(blank=True, help_text="JSON formatted extra metadata")

    class Meta:
        unique_together = ['tag', 'name', 'version']

    def __str__(self):
        return f"{self.name} v{self.version}"


class DataField(models.Model):
    """Field definition within a DataSchema."""
    DATA_TYPE_CHOICES = [
        ('int', 'Integer'),
        ('float', 'Float'),
        ('str', 'String'),
        ('bool', 'Boolean'),
        ('datetime', 'DateTime'),
    ]

    data_schema = models.ForeignKey(DataSchema, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200, blank=True)
    data_type = models.CharField(max_length=50, choices=DATA_TYPE_CHOICES)
    unit = models.CharField(max_length=50, blank=True, null=True)
    is_required = models.BooleanField(default=False)
    allow_null = models.BooleanField(default=True)
    default_value = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ['data_schema', 'name']
        ordering = ['order']

    def __str__(self):
        return f"{self.data_schema.name}.{self.name}"


class Dataset(BaseModel):
    """Dataset container."""
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('validating', 'Validating'),
        ('validated', 'Validated'),
        ('invalid', 'Invalid'),
        ('archived', 'Archived'),
    ]
    SOURCE_TYPE_CHOICES = [
        ('csv_upload', 'CSV Upload'),
        ('external_system', 'External System'),
        ('manual', 'Manual'),
    ]

    name = models.CharField(max_length=200)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='datasets')
    data_schema = models.ForeignKey(DataSchema, on_delete=models.SET_NULL, null=True, blank=True, related_name='datasets')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    num_records = models.BigIntegerField(null=True, blank=True)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPE_CHOICES, default='csv_upload')
    source_info = models.TextField(blank=True, help_text="JSON formatted source information")
    ingested_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class DatasetFile(models.Model):
    """File associated with a Dataset."""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='files')
    file_path = models.CharField(max_length=500)
    file_format = models.CharField(max_length=50, default='csv')
    filesize = models.BigIntegerField(null=True, blank=True)
    checksum = models.CharField(max_length=128, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.dataset.name}: {self.file_path}"


class DatasetProfile(models.Model):
    """Profile/statistics for a Dataset."""
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name='profile')
    profile_json = models.TextField(blank=True, help_text="JSON formatted profile data (min, max, mean, null_count, distinct_count per column)")
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile for {self.dataset.name}"


class AuditLog(models.Model):
    """Audit log for important operations."""
    event_type = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    target_type = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100)
    message = models.TextField()
    payload = models.TextField(blank=True, help_text="JSON formatted payload data")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type}: {self.target_type} ({self.target_id})"

