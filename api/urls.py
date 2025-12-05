from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Core endpoints
router.register(r'tags', views.TagViewSet)
router.register(r'schemas', views.DataSchemaViewSet)
router.register(r'fields', views.DataFieldViewSet)
router.register(r'datasets', views.DatasetViewSet)
router.register(r'dataset-files', views.DatasetFileViewSet)
router.register(r'dataset-profiles', views.DatasetProfileViewSet)

# Analysis endpoints
router.register(r'analysis-templates', views.AnalysisTemplateViewSet)
router.register(r'analysis-runs', views.AnalysisRunViewSet)

# MLOps endpoints
router.register(r'models', views.MLModelViewSet)
router.register(r'model-versions', views.MLModelVersionViewSet)
router.register(r'training-runs', views.MLTrainingRunViewSet)

# Jobs endpoints
router.register(r'jobs', views.JobViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('predict/', views.predict, name='predict'),
]
