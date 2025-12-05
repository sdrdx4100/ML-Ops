"""
Analysis application services for running analysis pipelines.
"""
import importlib
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import AnalysisRun, AnalysisTemplate
from core.models import Dataset
from core.services import create_audit_log

User = get_user_model()


def run_analysis(analysis_run_id: int) -> Dict[str, Any]:
    """
    Execute an analysis run.
    
    This function:
    1. Updates the AnalysisRun status to 'running'
    2. Loads the analysis function based on template.code_identifier
    3. Executes the analysis on the dataset
    4. Updates the AnalysisRun with results
    
    Args:
        analysis_run_id: ID of the AnalysisRun to execute
    
    Returns:
        Dictionary with execution results
    """
    analysis_run = AnalysisRun.objects.get(id=analysis_run_id)
    
    # Update status to running
    analysis_run.status = 'running'
    analysis_run.started_at = timezone.now()
    analysis_run.save()
    
    log_messages = []
    result_summary = {}
    
    try:
        log_messages.append(f"Starting analysis run {analysis_run_id}")
        log_messages.append(f"Template: {analysis_run.template.name}")
        
        # Get the code identifier
        code_identifier = analysis_run.template.code_identifier
        
        if code_identifier:
            # Try to dynamically import and run the analysis function
            try:
                module_path, func_name = code_identifier.rsplit('.', 1)
                module = importlib.import_module(module_path)
                analysis_func = getattr(module, func_name)
                
                # Parse parameters
                params = {}
                if analysis_run.parameters:
                    params = json.loads(analysis_run.parameters)
                
                # Run the analysis
                result_summary = analysis_func(analysis_run.dataset, params)
                log_messages.append(f"Analysis function {code_identifier} executed successfully")
                
            except (ImportError, AttributeError) as e:
                log_messages.append(f"Could not load analysis function: {e}")
                # Fall back to default analysis
                result_summary = _run_default_analysis(analysis_run.dataset, log_messages)
        else:
            # Run default analysis
            result_summary = _run_default_analysis(analysis_run.dataset, log_messages)
        
        # Update the run with success
        analysis_run.status = 'success'
        analysis_run.result_summary = json.dumps(result_summary)
        analysis_run.finished_at = timezone.now()
        analysis_run.log = '\n'.join(log_messages)
        analysis_run.save()
        
        # Create audit log
        create_audit_log(
            event_type='analysis_run',
            user=analysis_run.created_by,
            target_type='AnalysisRun',
            target_id=str(analysis_run_id),
            message=f'Analysis "{analysis_run.template.name}" completed successfully',
            payload=json.dumps({'status': 'success', 'dataset_id': analysis_run.dataset.id if analysis_run.dataset else None})
        )
        
        return {
            'status': 'success',
            'result_summary': result_summary,
            'log': log_messages
        }
        
    except Exception as e:
        log_messages.append(f"Error during analysis: {str(e)}")
        
        analysis_run.status = 'failed'
        analysis_run.finished_at = timezone.now()
        analysis_run.log = '\n'.join(log_messages)
        analysis_run.save()
        
        return {
            'status': 'failed',
            'error': str(e),
            'log': log_messages
        }


def _run_default_analysis(dataset: Optional[Dataset], log_messages: list) -> Dict[str, Any]:
    """
    Run a default basic statistics analysis on a dataset.
    
    Args:
        dataset: Dataset to analyze
        log_messages: List to append log messages to
    
    Returns:
        Dictionary with analysis results
    """
    import csv
    from typing import List
    
    result = {
        'type': 'basic_stats',
        'columns': {},
        'row_count': 0,
        'column_count': 0
    }
    
    if not dataset:
        log_messages.append("No dataset provided")
        return result
    
    dataset_file = dataset.files.filter(file_format='csv').first()
    if not dataset_file:
        log_messages.append("No CSV file found in dataset")
        return result
    
    if not os.path.exists(dataset_file.file_path):
        log_messages.append(f"File not found: {dataset_file.file_path}")
        return result
    
    log_messages.append(f"Analyzing file: {dataset_file.file_path}")
    
    try:
        with open(dataset_file.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []
            result['column_count'] = len(columns)
            
            # Initialize column stats
            column_values: Dict[str, List[Any]] = {col: [] for col in columns}
            
            # Collect values
            row_count = 0
            for row in reader:
                row_count += 1
                for col in columns:
                    value = row.get(col, '')
                    if value:
                        column_values[col].append(value)
            
            result['row_count'] = row_count
            log_messages.append(f"Processed {row_count} rows, {len(columns)} columns")
            
            # Calculate basic stats per column
            for col, values in column_values.items():
                col_stats = {
                    'count': len(values),
                    'null_count': row_count - len(values),
                    'distinct_count': len(set(values))
                }
                
                # Try numeric stats
                numeric_values: List[float] = []
                for v in values:
                    try:
                        numeric_values.append(float(v))
                    except (ValueError, TypeError):
                        pass
                
                if numeric_values:
                    col_stats['min'] = min(numeric_values)
                    col_stats['max'] = max(numeric_values)
                    col_stats['mean'] = sum(numeric_values) / len(numeric_values)
                    col_stats['sum'] = sum(numeric_values)
                
                result['columns'][col] = col_stats
        
        log_messages.append("Analysis completed successfully")
        
    except Exception as e:
        log_messages.append(f"Error reading file: {str(e)}")
        result['error'] = str(e)
    
    return result


def create_analysis_run(
    template_id: int,
    dataset_id: int,
    parameters: Optional[Dict[str, Any]] = None,
    created_by: Optional[User] = None
) -> AnalysisRun:
    """
    Create a new analysis run.
    
    Args:
        template_id: ID of the AnalysisTemplate to use
        dataset_id: ID of the Dataset to analyze
        parameters: Optional parameters for the analysis
        created_by: User creating the run
    
    Returns:
        Created AnalysisRun instance
    """
    template = AnalysisTemplate.objects.get(id=template_id)
    dataset = Dataset.objects.get(id=dataset_id)
    
    params_json = json.dumps(parameters) if parameters else ''
    
    analysis_run = AnalysisRun.objects.create(
        template=template,
        dataset=dataset,
        status='pending',
        parameters=params_json,
        created_by=created_by
    )
    
    return analysis_run
