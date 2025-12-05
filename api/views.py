import os
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

from core.models import Tag, DataSchema, DataField, Dataset, DatasetFile, DatasetProfile, AuditLog
from analysis.models import AnalysisTemplate, AnalysisRun
from mlops.models import MLModel, MLModelVersion, MLTrainingRun
from jobs.models import Job
from .serializers import (
    TagSerializer, DataSchemaSerializer, DataFieldSerializer,
    DatasetSerializer, DatasetFileSerializer, DatasetProfileSerializer,
    AuditLogSerializer,
    AnalysisTemplateSerializer, AnalysisRunSerializer,
    MLModelSerializer, MLModelVersionSerializer, MLTrainingRunSerializer,
    JobSerializer, PredictRequestSerializer, PredictResponseSerializer,
    ValidationResultSerializer, FileUploadSerializer,
)


# Core ViewSets
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']


class DataSchemaViewSet(viewsets.ModelViewSet):
    queryset = DataSchema.objects.all()
    serializer_class = DataSchemaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tag', 'is_active', 'is_default']


class DataFieldViewSet(viewsets.ModelViewSet):
    queryset = DataField.objects.all()
    serializer_class = DataFieldSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['data_schema']


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tag', 'status', 'source_type']

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate the dataset against its schema."""
        from core.services import validate_dataset
        
        result = validate_dataset(int(pk))
        serializer = ValidationResultSerializer(result)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def profile(self, request, pk=None):
        """Generate profile statistics for the dataset."""
        from core.services import generate_dataset_profile
        
        profile = generate_dataset_profile(int(pk))
        serializer = DatasetProfileSerializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request, pk=None):
        """Upload a file to the dataset."""
        from core.services import add_dataset_file
        
        dataset = self.get_object()
        file_serializer = FileUploadSerializer(data=request.data)
        
        if not file_serializer.is_valid():
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = file_serializer.validated_data['file']
        file_format = file_serializer.validated_data.get('file_format', 'csv')
        order = file_serializer.validated_data.get('order', 0)
        
        # Save file to disk
        upload_dir = os.path.join(settings.BASE_DIR, 'uploads', str(dataset.id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Create DatasetFile record
        dataset_file = add_dataset_file(
            dataset_id=dataset.id,
            file_path=file_path,
            file_format=file_format,
            order=order
        )
        
        serializer = DatasetFileSerializer(dataset_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DatasetFileViewSet(viewsets.ModelViewSet):
    queryset = DatasetFile.objects.all()
    serializer_class = DatasetFileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dataset', 'file_format']


class DatasetProfileViewSet(viewsets.ModelViewSet):
    queryset = DatasetProfile.objects.all()
    serializer_class = DatasetProfileSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event_type', 'target_type']


# Analysis ViewSets
class AnalysisTemplateViewSet(viewsets.ModelViewSet):
    queryset = AnalysisTemplate.objects.all()
    serializer_class = AnalysisTemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tag', 'is_active']


class AnalysisRunViewSet(viewsets.ModelViewSet):
    queryset = AnalysisRun.objects.all()
    serializer_class = AnalysisRunSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['template', 'dataset', 'status']

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute the analysis run."""
        from analysis.services import run_analysis
        from jobs.services import create_job, execute_job
        
        # Create a job for this analysis run
        job = create_job(
            job_type='analysis_run',
            target_id=str(pk)
        )
        
        # Execute the job synchronously
        result = execute_job(job.id)
        
        # Refresh the analysis run
        analysis_run = self.get_object()
        serializer = self.get_serializer(analysis_run)
        
        return Response({
            'analysis_run': serializer.data,
            'job_result': result
        })


# MLOps ViewSets
class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tag', 'task_type', 'is_active']


class MLModelVersionViewSet(viewsets.ModelViewSet):
    queryset = MLModelVersion.objects.all()
    serializer_class = MLModelVersionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['model', 'status']

    @action(detail=True, methods=['post'])
    def train(self, request, pk=None):
        """Train the model version."""
        from mlops.services import train_model
        from jobs.services import create_job, execute_job
        
        # Create a job for this training
        job = create_job(
            job_type='ml_training',
            target_id=str(pk)
        )
        
        # Execute the job synchronously
        result = execute_job(job.id)
        
        # Refresh the model version
        model_version = self.get_object()
        serializer = self.get_serializer(model_version)
        
        return Response({
            'model_version': serializer.data,
            'job_result': result
        })


class MLTrainingRunViewSet(viewsets.ModelViewSet):
    queryset = MLTrainingRun.objects.all()
    serializer_class = MLTrainingRunSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['model_version', 'status']


# Jobs ViewSet
class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['job_type', 'status', 'queue']


# Predict endpoint
@api_view(['POST'])
def predict(request):
    """
    Simple prediction endpoint.
    Accepts tag or model_version_id and input data.
    Returns prediction results.
    """
    from mlops.services import predict as mlops_predict
    
    serializer = PredictRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    tag = serializer.validated_data.get('tag')
    model_version_id = serializer.validated_data.get('model_version_id')
    inputs = serializer.validated_data.get('inputs', [])

    result = mlops_predict(
        tag_name=tag,
        model_version_id=model_version_id,
        inputs=inputs
    )

    if 'error' in result and result['error']:
        return Response(result, status=status.HTTP_404_NOT_FOUND)

    response_serializer = PredictResponseSerializer(result)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


