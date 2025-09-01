import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'daily-database-backup': {
        'task': 'core.tasks.daily_backup',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'cleanup-old-backups': {
        'task': 'core.tasks.cleanup_backups',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    'health-check': {
        'task': 'core.tasks.health_check',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'key-rotation-check': {
        'task': 'core.tasks.check_key_rotation',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
}

# Configure task routing
app.conf.task_routes = {
    'core.tasks.daily_backup': {'queue': 'backup'},
    'core.tasks.cleanup_backups': {'queue': 'maintenance'},
    'core.tasks.health_check': {'queue': 'monitoring'},
    'core.tasks.check_key_rotation': {'queue': 'security'},
}

# Configure task settings
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')