# ML-Ops: Meta Analytics Platform

A Django-based tag-driven metadata, data management, analysis, and machine learning platform.

## Overview

This platform is a "tag-driven metadata and data analysis/ML platform" that provides:

- **Tag-based Organization**: Categorize data by type, schema, and ML task using tags
- **Schema Management**: Define and version data schemas with field definitions
- **Dataset Management**: Register, validate, and profile datasets
- **Analysis Pipelines**: Create and execute analysis templates on datasets
- **ML Model Management**: Train, version, and deploy machine learning models
- **Job Queue**: Manage asynchronous job execution (extensible to Celery)

## Project Structure

- **meta_analytics_platform/** - Django project settings
- **core/** - Core models: Tag, DataSchema, DataField, Dataset, DatasetFile, DatasetProfile, AuditLog
- **analysis/** - Analysis models: AnalysisTemplate, AnalysisRun
- **mlops/** - ML models: MLModel, MLModelVersion, MLTrainingRun
- **jobs/** - Job management: Job
- **api/** - DRF REST API for all models

## Quick Start

### 1. Create Python Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
python manage.py migrate
```

### 4. Create a Superuser (for Admin access)

```bash
python manage.py createsuperuser
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The server will start at: http://127.0.0.1:8000/

## URLs

- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Root**: http://127.0.0.1:8000/api/

## API Endpoints

All endpoints are available at `/api/`:

### Core Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/tags/` | Tag CRUD (filter by: category, is_active) |
| `/api/schemas/` | DataSchema CRUD (filter by: tag, is_active, is_default) |
| `/api/fields/` | DataField CRUD (filter by: data_schema) |
| `/api/datasets/` | Dataset CRUD (filter by: tag, status, source_type) |
| `/api/datasets/{id}/validate/` | POST: Validate dataset against schema |
| `/api/datasets/{id}/profile/` | POST: Generate dataset statistics |
| `/api/datasets/{id}/upload/` | POST: Upload a file to dataset |
| `/api/dataset-files/` | DatasetFile CRUD |
| `/api/dataset-profiles/` | DatasetProfile CRUD |
| `/api/audit-logs/` | AuditLog read-only (filter by: event_type, target_type) |

### Analysis Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/analysis-templates/` | AnalysisTemplate CRUD (filter by: tag, is_active) |
| `/api/analysis-runs/` | AnalysisRun CRUD (filter by: template, dataset, status) |
| `/api/analysis-runs/{id}/execute/` | POST: Execute analysis run |

### MLOps Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/models/` | MLModel CRUD (filter by: tag, task_type, is_active) |
| `/api/model-versions/` | MLModelVersion CRUD (filter by: model, status) |
| `/api/model-versions/{id}/train/` | POST: Train model version |
| `/api/training-runs/` | MLTrainingRun CRUD (filter by: model_version, status) |

### Prediction & Jobs

| Endpoint | Description |
|----------|-------------|
| `/api/predict/` | POST: Make predictions (requires tag or model_version_id) |
| `/api/jobs/` | Job read-only (filter by: job_type, status, queue) |

## Database Configuration

The project uses SQLite by default for development. To switch to PostgreSQL:

```bash
export DATABASE_ENGINE=django.db.backends.postgresql
export DATABASE_NAME=your_db_name
export DATABASE_USER=your_user
export DATABASE_PASSWORD=your_password
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Development key |
| `DJANGO_DEBUG` | Debug mode | True |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | Empty |
| `DATABASE_ENGINE` | Database engine | django.db.backends.sqlite3 |
| `DATABASE_NAME` | Database name | db.sqlite3 |
| `DATABASE_USER` | Database user (PostgreSQL) | postgres |
| `DATABASE_PASSWORD` | Database password (PostgreSQL) | Empty |
| `DATABASE_HOST` | Database host (PostgreSQL) | localhost |
| `DATABASE_PORT` | Database port (PostgreSQL) | 5432 |

## Architecture

### Services Layer

Business logic is encapsulated in service modules:

- `core/services.py` - Dataset registration, validation, profiling
- `analysis/services.py` - Analysis execution
- `mlops/services.py` - Model training, prediction
- `jobs/services.py` - Job creation and execution

### Future Extensions

- **Celery Integration**: The jobs app is designed to easily integrate with Celery for async task execution
- **DuckDB/Polars**: The services layer can be extended to use DuckDB/Polars for advanced data processing
- **PyTorch/sklearn**: The ML services can be extended with real model training

## Example Usage

### Create a Tag

```bash
curl -X POST http://127.0.0.1:8000/api/tags/ \
  -H "Content-Type: application/json" \
  -d '{"name": "vehicle_dynamics_v1", "display_name": "Vehicle Dynamics", "category": "dataset"}'
```

### Create a Schema

```bash
curl -X POST http://127.0.0.1:8000/api/schemas/ \
  -H "Content-Type: application/json" \
  -d '{"name": "vehicle_schema", "tag": 1, "version": "1.0", "is_default": true}'
```

### Create a Dataset

```bash
curl -X POST http://127.0.0.1:8000/api/datasets/ \
  -H "Content-Type: application/json" \
  -d '{"name": "test_dataset", "tag": 1, "data_schema": 1}'
```

### Make a Prediction

```bash
curl -X POST http://127.0.0.1:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{"tag": "vehicle_dynamics_v1", "inputs": [{"speed": 60}]}'
```