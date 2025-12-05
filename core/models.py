from django.db import models


class Tag(models.Model):
    """Tag for categorizing and organizing data."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DataSchema(models.Model):
    """Schema definition for datasets."""
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50, default='1.0')
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='schemas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['name', 'version']

    def __str__(self):
        return f"{self.name} v{self.version}"


class DataField(models.Model):
    """Field definition within a DataSchema."""
    FIELD_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('datetime', 'DateTime'),
        ('json', 'JSON'),
    ]
    schema = models.ForeignKey(DataSchema, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['schema', 'name']

    def __str__(self):
        return f"{self.schema.name}.{self.name}"


class Dataset(models.Model):
    """Dataset container."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    schema = models.ForeignKey(DataSchema, on_delete=models.SET_NULL, null=True, blank=True, related_name='datasets')
    tags = models.ManyToManyField(Tag, blank=True, related_name='datasets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DatasetFile(models.Model):
    """File associated with a Dataset."""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='files')
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    file_format = models.CharField(max_length=50, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dataset.name}: {self.file_path}"


class DatasetProfile(models.Model):
    """Profile/statistics for a Dataset."""
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name='profile')
    row_count = models.BigIntegerField(default=0)
    column_count = models.IntegerField(default=0)
    profile_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.dataset.name}"

