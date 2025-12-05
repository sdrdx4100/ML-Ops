from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Tag, DataSchema, DataField, Dataset, DatasetFile, DatasetProfile
from analysis.models import AnalysisTemplate, AnalysisRun
from mlops.models import MLModel, MLModelVersion, MLTrainingRun
from jobs.models import Job
from .serializers import (
    TagSerializer, DataSchemaSerializer, DataFieldSerializer,
    DatasetSerializer, DatasetFileSerializer, DatasetProfileSerializer,
    AnalysisTemplateSerializer, AnalysisRunSerializer,
    MLModelSerializer, MLModelVersionSerializer, MLTrainingRunSerializer,
    JobSerializer, PredictRequestSerializer, PredictResponseSerializer,
)


# Core ViewSets
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class DataSchemaViewSet(viewsets.ModelViewSet):
    queryset = DataSchema.objects.all()
    serializer_class = DataSchemaSerializer


class DataFieldViewSet(viewsets.ModelViewSet):
    queryset = DataField.objects.all()
    serializer_class = DataFieldSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer


class DatasetFileViewSet(viewsets.ModelViewSet):
    queryset = DatasetFile.objects.all()
    serializer_class = DatasetFileSerializer


class DatasetProfileViewSet(viewsets.ModelViewSet):
    queryset = DatasetProfile.objects.all()
    serializer_class = DatasetProfileSerializer


# Analysis ViewSets
class AnalysisTemplateViewSet(viewsets.ModelViewSet):
    queryset = AnalysisTemplate.objects.all()
    serializer_class = AnalysisTemplateSerializer


class AnalysisRunViewSet(viewsets.ModelViewSet):
    queryset = AnalysisRun.objects.all()
    serializer_class = AnalysisRunSerializer


# MLOps ViewSets
class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer


class MLModelVersionViewSet(viewsets.ModelViewSet):
    queryset = MLModelVersion.objects.all()
    serializer_class = MLModelVersionSerializer


class MLTrainingRunViewSet(viewsets.ModelViewSet):
    queryset = MLTrainingRun.objects.all()
    serializer_class = MLTrainingRunSerializer


# Jobs ViewSet
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


# Predict endpoint
@api_view(['POST'])
def predict(request):
    """
    Simple prediction endpoint.
    Accepts model_id, optional version, and input data.
    Returns a mock prediction result.
    """
    serializer = PredictRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    model_id = serializer.validated_data['model_id']
    version = serializer.validated_data.get('version')
    input_data = serializer.validated_data['data']

    # Get the model
    try:
        ml_model = MLModel.objects.get(id=model_id)
    except MLModel.DoesNotExist:
        return Response(
            {'error': f'Model with id {model_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get the model version
    if version:
        try:
            model_version = MLModelVersion.objects.get(model=ml_model, version=version)
        except MLModelVersion.DoesNotExist:
            return Response(
                {'error': f'Version {version} not found for model {ml_model.name}'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        # Try to get the active version
        model_version = MLModelVersion.objects.filter(model=ml_model, is_active=True).first()
        if not model_version:
            # Get the latest version
            model_version = MLModelVersion.objects.filter(model=ml_model).order_by('-created_at').first()
        if not model_version:
            return Response(
                {'error': f'No version found for model {ml_model.name}'},
                status=status.HTTP_404_NOT_FOUND
            )

    # Mock prediction result
    prediction_result = {
        'model_id': ml_model.id,
        'model_name': ml_model.name,
        'version': model_version.version,
        'prediction': {
            'result': 'mock_prediction',
            'confidence': 0.95,
            'input_received': input_data
        },
        'status': 'success'
    }

    response_serializer = PredictResponseSerializer(prediction_result)
    return Response(response_serializer.data, status=status.HTTP_200_OK)

