from rest_framework import serializers
from core.models import Tag, DataSchema, DataField, Dataset, DatasetFile, DatasetProfile
from analysis.models import AnalysisTemplate, AnalysisRun
from mlops.models import MLModel, MLModelVersion, MLTrainingRun
from jobs.models import Job


# Core serializers
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class DataFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataField
        fields = '__all__'


class DataSchemaSerializer(serializers.ModelSerializer):
    fields = DataFieldSerializer(many=True, read_only=True)

    class Meta:
        model = DataSchema
        fields = '__all__'


class DatasetFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetFile
        fields = '__all__'


class DatasetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetProfile
        fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):
    files = DatasetFileSerializer(many=True, read_only=True)
    profile = DatasetProfileSerializer(read_only=True)

    class Meta:
        model = Dataset
        fields = '__all__'


# Analysis serializers
class AnalysisTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisTemplate
        fields = '__all__'


class AnalysisRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisRun
        fields = '__all__'


# MLOps serializers
class MLModelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModelVersion
        fields = '__all__'


class MLModelSerializer(serializers.ModelSerializer):
    versions = MLModelVersionSerializer(many=True, read_only=True)

    class Meta:
        model = MLModel
        fields = '__all__'


class MLTrainingRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLTrainingRun
        fields = '__all__'


# Jobs serializers
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


# Predict endpoint serializers
class PredictRequestSerializer(serializers.Serializer):
    model_id = serializers.IntegerField(help_text="ID of the ML model to use for prediction")
    version = serializers.CharField(required=False, help_text="Model version (optional, uses active version if not specified)")
    data = serializers.JSONField(help_text="Input data for prediction")


class PredictResponseSerializer(serializers.Serializer):
    model_id = serializers.IntegerField()
    model_name = serializers.CharField()
    version = serializers.CharField()
    prediction = serializers.JSONField()
    status = serializers.CharField()
