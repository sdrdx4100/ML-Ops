"""
MLOps application services for model training and prediction.
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import MLModel, MLModelVersion, MLTrainingRun
from core.models import Dataset
from core.services import create_audit_log

User = get_user_model()


def train_model(model_version_id: int) -> Dict[str, Any]:
    """
    Train a model version.
    
    This function:
    1. Creates or updates the MLTrainingRun
    2. Performs dummy training
    3. Updates metrics and artifact path
    
    Args:
        model_version_id: ID of the MLModelVersion to train
    
    Returns:
        Dictionary with training results
    """
    model_version = MLModelVersion.objects.get(id=model_version_id)
    
    # Create or get training run
    training_run = MLTrainingRun.objects.filter(
        model_version=model_version,
        status__in=['pending', 'running']
    ).first()
    
    if not training_run:
        training_run = MLTrainingRun.objects.create(
            model_version=model_version,
            status='pending'
        )
    
    # Update status to running
    training_run.status = 'running'
    training_run.started_at = timezone.now()
    training_run.save()
    
    model_version.status = 'training'
    model_version.save()
    
    log_messages = []
    
    try:
        log_messages.append(f"Starting training for model version {model_version_id}")
        log_messages.append(f"Model: {model_version.model.name}")
        log_messages.append(f"Version: {model_version.version}")
        
        # Parse hyperparameters
        hyperparams = {}
        if training_run.hyperparams:
            try:
                hyperparams = json.loads(training_run.hyperparams)
            except json.JSONDecodeError:
                log_messages.append("Warning: Could not parse hyperparameters")
        
        log_messages.append(f"Hyperparameters: {hyperparams}")
        
        # Perform dummy training
        log_messages.append("Performing training (dummy implementation)...")
        
        # Simulate training metrics
        metrics = {
            'accuracy': 0.95,
            'precision': 0.94,
            'recall': 0.93,
            'f1_score': 0.935,
            'loss': 0.05,
            'training_time_seconds': 10.5
        }
        
        # Create artifact directory if it doesn't exist
        artifact_dir = os.path.join(settings.BASE_DIR, 'models')
        os.makedirs(artifact_dir, exist_ok=True)
        
        # Create dummy artifact file
        model_name_safe = model_version.model.name.replace(' ', '_').lower()
        artifact_filename = f"{model_name_safe}_v{model_version.version}.pkl"
        artifact_path = os.path.join('models', artifact_filename)
        full_artifact_path = os.path.join(settings.BASE_DIR, artifact_path)
        
        # Write dummy model file
        with open(full_artifact_path, 'w') as f:
            f.write(json.dumps({
                'model_type': model_version.model.task_type,
                'version': model_version.version,
                'trained_at': timezone.now().isoformat(),
                'metrics': metrics
            }))
        
        log_messages.append(f"Model artifact saved to: {artifact_path}")
        
        # Update model version
        model_version.status = 'ready'
        model_version.artifact_path = artifact_path
        model_version.metrics = json.dumps(metrics)
        model_version.save()
        
        # Update training run
        training_run.status = 'success'
        training_run.finished_at = timezone.now()
        training_run.log = '\n'.join(log_messages)
        training_run.save()
        
        # Create audit log
        create_audit_log(
            event_type='model_trained',
            user=training_run.created_by,
            target_type='MLModelVersion',
            target_id=str(model_version_id),
            message=f'Model "{model_version.model.name}" v{model_version.version} trained successfully',
            payload=json.dumps({'metrics': metrics})
        )
        
        log_messages.append("Training completed successfully")
        
        return {
            'status': 'success',
            'metrics': metrics,
            'artifact_path': artifact_path,
            'log': log_messages
        }
        
    except Exception as e:
        log_messages.append(f"Error during training: {str(e)}")
        
        training_run.status = 'failed'
        training_run.finished_at = timezone.now()
        training_run.log = '\n'.join(log_messages)
        training_run.save()
        
        model_version.status = 'failed'
        model_version.save()
        
        return {
            'status': 'failed',
            'error': str(e),
            'log': log_messages
        }


def predict(
    tag_name: Optional[str] = None,
    model_version_id: Optional[int] = None,
    inputs: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Make predictions using a model.
    
    Args:
        tag_name: Tag name to find the default model
        model_version_id: Specific model version ID to use
        inputs: List of input data dictionaries
    
    Returns:
        Dictionary with predictions
    """
    if inputs is None:
        inputs = []
    
    # Get model version
    model_version = None
    
    if model_version_id:
        model_version = MLModelVersion.objects.filter(
            id=model_version_id,
            status='ready'
        ).first()
    elif tag_name:
        # Find default ready model for this tag
        from core.models import Tag
        tag = Tag.objects.filter(name=tag_name).first()
        if tag:
            model = MLModel.objects.filter(tag=tag, is_active=True).first()
            if model:
                model_version = model.versions.filter(status='ready').order_by('-created_at').first()
    
    if not model_version:
        return {
            'error': 'No ready model found',
            'predictions': [],
            'used_model_version': None
        }
    
    # Perform dummy prediction
    predictions = []
    for input_data in inputs:
        prediction = {
            'input': input_data,
            'output': {
                'prediction': 0.5,  # Dummy prediction
                'confidence': 0.95
            }
        }
        predictions.append(prediction)
    
    return {
        'predictions': predictions,
        'used_model_version': {
            'id': model_version.id,
            'model_name': model_version.model.name,
            'version': model_version.version
        }
    }


def create_model_version(
    model_id: int,
    version: str,
    dataset_id: Optional[int] = None,
    hyperparams: Optional[Dict[str, Any]] = None,
    description: str = "",
    created_by: Optional[User] = None
) -> MLModelVersion:
    """
    Create a new model version with an associated training run.
    
    Args:
        model_id: ID of the parent MLModel
        version: Version string
        dataset_id: Optional ID of training dataset
        hyperparams: Optional hyperparameters for training
        description: Version description
        created_by: User creating the version
    
    Returns:
        Created MLModelVersion instance
    """
    model = MLModel.objects.get(id=model_id)
    
    trained_on_dataset = None
    if dataset_id:
        trained_on_dataset = Dataset.objects.get(id=dataset_id)
    
    model_version = MLModelVersion.objects.create(
        model=model,
        version=version,
        status='training',
        trained_on_dataset=trained_on_dataset,
        description=description
    )
    
    # Create associated training run
    hyperparams_json = json.dumps(hyperparams) if hyperparams else ''
    
    MLTrainingRun.objects.create(
        model_version=model_version,
        status='pending',
        hyperparams=hyperparams_json,
        created_by=created_by
    )
    
    return model_version
