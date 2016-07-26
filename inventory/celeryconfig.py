from datetime import timedelta
from celery.schedules import crontab

BROKER_URL = 'mongodb://localhost:27017/inventory'
CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/inventory'

CELERY_TIMEZONE = 'UTC'

