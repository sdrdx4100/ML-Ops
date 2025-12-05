"""
Jobs application services for managing job execution.
"""
import json
from typing import Optional, Dict, Any

from django.utils import timezone

from .models import Job


def create_job(
    job_type: str,
    target_id: str,
    priority: int = 0,
    queue: str = 'default'
) -> Job:
    """
    Create a new job.
    
    Args:
        job_type: Type of job (analysis_run, ml_training)
        target_id: ID of the target object
        priority: Job priority (higher = more important)
        queue: Queue name for the job
    
    Returns:
        Created Job instance
    """
    return Job.objects.create(
        job_type=job_type,
        target_id=target_id,
        status='pending',
        priority=priority,
        queue=queue
    )


def execute_job(job_id: int) -> Dict[str, Any]:
    """
    Execute a job synchronously.
    
    This function dispatches to the appropriate service based on job_type.
    
    Args:
        job_id: ID of the job to execute
    
    Returns:
        Dictionary with execution results
    """
    job = Job.objects.get(id=job_id)
    
    job.status = 'running'
    job.started_at = timezone.now()
    job.save()
    
    log_messages = []
    
    try:
        log_messages.append(f"Starting job {job_id}")
        log_messages.append(f"Job type: {job.job_type}")
        log_messages.append(f"Target ID: {job.target_id}")
        
        result = {}
        
        if job.job_type == 'analysis_run':
            from analysis.services import run_analysis
            result = run_analysis(int(job.target_id))
            
        elif job.job_type == 'ml_training':
            from mlops.services import train_model
            result = train_model(int(job.target_id))
            
        else:
            raise ValueError(f"Unknown job type: {job.job_type}")
        
        log_messages.append(f"Job completed with status: {result.get('status', 'unknown')}")
        
        job.status = 'success' if result.get('status') == 'success' else 'failed'
        job.finished_at = timezone.now()
        job.log = '\n'.join(log_messages)
        job.save()
        
        return {
            'status': job.status,
            'result': result,
            'log': log_messages
        }
        
    except Exception as e:
        log_messages.append(f"Error executing job: {str(e)}")
        
        job.status = 'failed'
        job.finished_at = timezone.now()
        job.log = '\n'.join(log_messages)
        job.save()
        
        return {
            'status': 'failed',
            'error': str(e),
            'log': log_messages
        }


def cancel_job(job_id: int) -> bool:
    """
    Cancel a pending or running job.
    
    Args:
        job_id: ID of the job to cancel
    
    Returns:
        True if job was cancelled, False otherwise
    """
    job = Job.objects.get(id=job_id)
    
    if job.status in ['pending', 'running']:
        job.status = 'canceled'
        job.finished_at = timezone.now()
        job.log = (job.log or '') + '\nJob cancelled by user'
        job.save()
        return True
    
    return False


def get_pending_jobs(queue: str = 'default', limit: int = 10) -> list:
    """
    Get pending jobs from a queue.
    
    Args:
        queue: Queue name
        limit: Maximum number of jobs to return
    
    Returns:
        List of pending Job instances
    """
    return list(Job.objects.filter(
        queue=queue,
        status='pending'
    ).order_by('-priority', 'created_at')[:limit])
