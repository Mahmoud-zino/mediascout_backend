import os

from celery import Celery
from celery.schedules import crontab

from api.tasks import test_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediaScout_django.settings')

app = Celery('mediaScout_django')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, test_task, name='add every 10')