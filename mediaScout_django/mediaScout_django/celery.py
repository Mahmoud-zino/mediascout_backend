import os

from celery import Celery
from celery.schedules import crontab

from api.tasks import update_youtube_videos

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
    sender.add_periodic_task(60.0, update_youtube_videos, name='update_youtube_videos_every_60')