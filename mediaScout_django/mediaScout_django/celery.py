import os

from celery import Celery
from celery.schedules import crontab

from api.tasks import test_task

# load django default settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediaScout_django.settings')

# add rabbitmq as broker
app = Celery('mediaScout_django', broker='amqp://guest:guest@rabbitmq:5672/')

app.config_from_object('django.conf:settings', namespace='CELERY')

# discover tasks with the tag @shared_task
app.autodiscover_tasks()

# configure tasks
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, test_task, name='add every 10')