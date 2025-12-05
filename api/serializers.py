from rest_framework import serializers
from core.models import Tag, DataSchema, DataField, Dataset, DatasetFile, DatasetProfile, AuditLog
from analysis.models import AnalysisTemplate, AnalysisRun
from mlops.models import MLModel, MLModelVersion, MLTrainingRun
from jobs.models import Job


# Core serializers
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DataFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataField
        fields = '__all__'


class DataSchemaSerializer(serializers.ModelSerializer):
    fields = DataFieldSerializer(many=True, read_only=True)

    class Meta:
        model = DataSchema
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class DatasetFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetFile
        fields = '__all__'
        read_only_fields = ['uploaded_at', 'filesize', 'checksum']


class DatasetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetProfile
        fields = '__all__'
        read_only_fields = ['generated_at']


class DatasetSerializer(serializers.ModelSerializer):
    files = DatasetFileSerializer(many=True, read_only=True)
    profile = DatasetProfileSerializer(read_only=True)

    class Meta:
        model = Dataset
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'num_records', 'ingested_at']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['created_at']


# Analysis serializers
class AnalysisTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisTemplate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AnalysisRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRun
        fields = '__all__'
        read_only_fields = ['created_at', 'started_at', 'finished_at', 'result_path', 'result_summary', 'log']


# MLOps serializers
class MLModelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModelVersion
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'artifact_path', 'metrics']


class MLModelSerializer(serializers.ModelSerializer):
    versions = MLModelVersionSerializer(many=True, read_only=True)

    class Meta:
        model = MLModel
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MLTrainingRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLTrainingRun
        fields = '__all__'
        read_only_fields = ['created_at', 'started_at', 'finished_at', 'log']


# Jobs serializers
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'started_at', 'finished_at', 'log']


# Predict endpoint serializers
class PredictRequestSerializer(serializers.Serializer):
    tag = serializers.CharField(
        required=False,
        help_text="Tag name to find default model"
    )
    model_version_id = serializers.IntegerField(
        required=False,
        help_text="Specific model version ID to use"
    )
    inputs = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of input data dictionaries"
    )

    def validate(self, data):
        if not data.get('tag') and not data.get('model_version_id'):
            raise serializers.ValidationError(
                "Either 'tag' or 'model_version_id' must be provided"
            )
        return data


class PredictResponseSerializer(serializers.Serializer):
    predictions = serializers.ListField()
    used_model_version = serializers.DictField(allow_null=True)
    error = serializers.CharField(required=False)


# Validation result serializer
class ValidationResultSerializer(serializers.Serializer):
    valid = serializers.BooleanField()
    errors = serializers.ListField(child=serializers.CharField())
    warnings = serializers.ListField(child=serializers.CharField())
    record_count = serializers.IntegerField()
    column_count = serializers.IntegerField()


# File upload serializer
class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    file_format = serializers.CharField(default='csv')
    order = serializers.IntegerField(default=0)

