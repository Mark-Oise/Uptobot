import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-monitors': {
        'task': 'apps.monitor.tasks.schedule_monitor_checks',
        'schedule': crontab(minute='*/1'),  # Run every minute
    },
    # 'process-batched-alerts': {
    #     'task': 'apps.alerts.tasks.process_batched_alerts',
    #     'schedule': 900.0,  # 15 minutes in seconds
    # },
    # 'send-alert-email': {
    #     'task': 'apps.alerts.tasks.send_alert_email',
    #     'schedule': 60.0,  # Run every minute
    # },
}