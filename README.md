# ML-Ops: Meta Analytics Platform

A Django-based tag-driven data analysis and ML platform.

## Project Structure

- **meta_analytics_platform/** - Django project settings
- **core/** - Core models: Tag, DataSchema, DataField, Dataset, DatasetFile, DatasetProfile
- **analysis/** - Analysis models: AnalysisTemplate, AnalysisRun
- **mlops/** - ML models: MLModel, MLModelVersion, MLTrainingRun
- **jobs/** - Job management: Job
- **api/** - DRF REST API for all models

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

All endpoints are available at `/api/`:

- `/api/tags/` - Tag CRUD
- `/api/schemas/` - DataSchema CRUD
- `/api/fields/` - DataField CRUD
- `/api/datasets/` - Dataset CRUD
- `/api/dataset-files/` - DatasetFile CRUD
- `/api/dataset-profiles/` - DatasetProfile CRUD
- `/api/analysis-templates/` - AnalysisTemplate CRUD
- `/api/analysis-runs/` - AnalysisRun CRUD
- `/api/models/` - MLModel CRUD
- `/api/model-versions/` - MLModelVersion CRUD
- `/api/training-runs/` - MLTrainingRun CRUD
- `/api/jobs/` - Job CRUD
- `/api/predict/` - Prediction endpoint

## Admin

Access the Django admin at `/admin/`

## Database

Uses SQLite by default (db.sqlite3)