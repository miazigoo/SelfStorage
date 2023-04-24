import os
from celery import Celery
from django.conf import settings
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SelfStorage.settings')

app = Celery('SelfStorage')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'send-notification-every-24-hours': {
        'task': 'storage.tasks.send_notification',
        'schedule': timedelta(seconds=60),
    },
}