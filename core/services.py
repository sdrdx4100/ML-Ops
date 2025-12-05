"""
Core application services for dataset management.
"""
import csv
import json
import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Dataset, DatasetFile, DatasetProfile, DataSchema, AuditLog

User = get_user_model()


def register_dataset(
    name: str,
    tag_id: int,
    data_schema_id: Optional[int] = None,
    description: str = "",
    source_type: str = "csv_upload",
    source_info: str = "",
    created_by: Optional[User] = None
) -> Dataset:
    """
    Register a new dataset with the given metadata.
    
    Args:
        name: Dataset name
        tag_id: FK to Tag
        data_schema_id: Optional FK to DataSchema
        description: Dataset description
        source_type: Source type (csv_upload, external_system, manual)
        source_info: JSON string with source information
        created_by: User who created the dataset
    
    Returns:
        Created Dataset instance
    """
    from .models import Tag, DataSchema
    
    tag = Tag.objects.get(id=tag_id)
    data_schema = None
    if data_schema_id:
        data_schema = DataSchema.objects.get(id=data_schema_id)
    
    dataset = Dataset.objects.create(
        name=name,
        tag=tag,
        data_schema=data_schema,
        description=description,
        source_type=source_type,
        source_info=source_info,
        status='registered',
        ingested_at=timezone.now(),
        created_by=created_by
    )
    
    # Create audit log
    create_audit_log(
        event_type='dataset_uploaded',
        user=created_by,
        target_type='Dataset',
        target_id=str(dataset.id),
        message=f'Dataset "{name}" registered',
        payload=json.dumps({'tag_id': tag_id, 'source_type': source_type})
    )
    
    return dataset


def add_dataset_file(
    dataset_id: int,
    file_path: str,
    file_format: str = "csv",
    order: int = 0
) -> DatasetFile:
    """
    Add a file to a dataset.
    
    Args:
        dataset_id: FK to Dataset
        file_path: Path to the file
        file_format: File format (csv, parquet, etc.)
        order: Order of the file in the dataset
    
    Returns:
        Created DatasetFile instance
    """
    dataset = Dataset.objects.get(id=dataset_id)
    
    # Calculate file size and checksum if file exists
    filesize = None
    checksum = None
    if os.path.exists(file_path):
        filesize = os.path.getsize(file_path)
        with open(file_path, 'rb') as f:
            checksum = hashlib.md5(f.read()).hexdigest()
    
    dataset_file = DatasetFile.objects.create(
        dataset=dataset,
        file_path=file_path,
        file_format=file_format,
        filesize=filesize,
        checksum=checksum,
        order=order
    )
    
    return dataset_file


def validate_dataset(dataset_id: int) -> Dict[str, Any]:
    """
    Validate a dataset against its schema.
    
    Args:
        dataset_id: ID of the dataset to validate
    
    Returns:
        Dictionary with validation results
    """
    dataset = Dataset.objects.get(id=dataset_id)
    dataset.status = 'validating'
    dataset.save()
    
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'record_count': 0,
        'column_count': 0
    }
    
    # Get the first CSV file
    dataset_file = dataset.files.filter(file_format='csv').first()
    if not dataset_file:
        validation_result['valid'] = False
        validation_result['errors'].append('No CSV file found in dataset')
        dataset.status = 'invalid'
        dataset.save()
        return validation_result
    
    if not os.path.exists(dataset_file.file_path):
        validation_result['valid'] = False
        validation_result['errors'].append(f'File not found: {dataset_file.file_path}')
        dataset.status = 'invalid'
        dataset.save()
        return validation_result
    
    try:
        with open(dataset_file.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []
            validation_result['column_count'] = len(columns)
            
            # Count records
            row_count = 0
            for _ in reader:
                row_count += 1
            validation_result['record_count'] = row_count
        
        # Validate against schema if available
        if dataset.data_schema:
            schema_fields = list(dataset.data_schema.fields.values_list('name', flat=True))
            required_fields = list(
                dataset.data_schema.fields.filter(is_required=True).values_list('name', flat=True)
            )
            
            # Check for missing required fields
            for field in required_fields:
                if field not in columns:
                    validation_result['errors'].append(f'Missing required field: {field}')
                    validation_result['valid'] = False
            
            # Check for extra fields not in schema
            for col in columns:
                if col not in schema_fields:
                    validation_result['warnings'].append(f'Extra field not in schema: {col}')
        
        # Update dataset
        dataset.num_records = validation_result['record_count']
        if validation_result['valid']:
            dataset.status = 'validated'
        else:
            dataset.status = 'invalid'
        dataset.save()
        
    except Exception as e:
        validation_result['valid'] = False
        validation_result['errors'].append(f'Validation error: {str(e)}')
        dataset.status = 'invalid'
        dataset.save()
    
    return validation_result


def generate_dataset_profile(dataset_id: int) -> DatasetProfile:
    """
    Generate a profile with basic statistics for a dataset.
    
    Args:
        dataset_id: ID of the dataset to profile
    
    Returns:
        Created or updated DatasetProfile instance
    """
    dataset = Dataset.objects.get(id=dataset_id)
    
    # Get the first CSV file
    dataset_file = dataset.files.filter(file_format='csv').first()
    if not dataset_file or not os.path.exists(dataset_file.file_path):
        # Create empty profile
        profile, _ = DatasetProfile.objects.update_or_create(
            dataset=dataset,
            defaults={
                'profile_json': json.dumps({'error': 'No valid CSV file found'}),
                'generated_at': timezone.now()
            }
        )
        return profile
    
    profile_data: Dict[str, Dict[str, Any]] = {}
    
    try:
        with open(dataset_file.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []
            
            # Initialize stats for each column
            for col in columns:
                profile_data[col] = {
                    'min': None,
                    'max': None,
                    'mean': None,
                    'null_count': 0,
                    'distinct_count': 0,
                    'values': []
                }
            
            # Collect values
            for row in reader:
                for col in columns:
                    value = row.get(col, '')
                    if value == '' or value is None:
                        profile_data[col]['null_count'] += 1
                    else:
                        profile_data[col]['values'].append(value)
            
            # Calculate statistics
            for col in columns:
                values = profile_data[col]['values']
                profile_data[col]['distinct_count'] = len(set(values))
                
                # Try to parse as numbers for min/max/mean
                numeric_values: List[float] = []
                for v in values:
                    try:
                        numeric_values.append(float(v))
                    except (ValueError, TypeError):
                        pass
                
                if numeric_values:
                    profile_data[col]['min'] = min(numeric_values)
                    profile_data[col]['max'] = max(numeric_values)
                    profile_data[col]['mean'] = sum(numeric_values) / len(numeric_values)
                elif values:
                    # For non-numeric, use string min/max
                    profile_data[col]['min'] = min(values)
                    profile_data[col]['max'] = max(values)
                
                # Remove raw values from final output
                del profile_data[col]['values']
    
    except Exception as e:
        profile_data = {'error': str(e)}
    
    profile, _ = DatasetProfile.objects.update_or_create(
        dataset=dataset,
        defaults={
            'profile_json': json.dumps(profile_data),
            'generated_at': timezone.now()
        }
    )
    
    return profile


def create_audit_log(
    event_type: str,
    target_type: str,
    target_id: str,
    message: str,
    user: Optional[User] = None,
    payload: str = ""
) -> AuditLog:
    """
    Create an audit log entry.
    
    Args:
        event_type: Type of event
        target_type: Type of target object
        target_id: ID of target object
        message: Human-readable message
        user: User who performed the action
        payload: JSON string with additional data
    
    Returns:
        Created AuditLog instance
    """
    return AuditLog.objects.create(
        event_type=event_type,
        user=user,
        target_type=target_type,
        target_id=target_id,
        message=message,
        payload=payload
    )
