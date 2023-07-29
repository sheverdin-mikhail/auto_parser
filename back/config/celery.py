import os
from celery import Celery
from datetime import timedelta
from kombu import Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'my-periodic-task': {
        'task': 'src.panel.tasks.reset_proxies',
        'schedule': timedelta(seconds=5),
        'options': {
            'queue': 'beat_queue'  # Имя очереди для задач Celery Beat
        }
    },
}

app.conf.task_queues = [
    Queue('default'),
    Queue('beat_queue')  # Очередь для задач Celery Beat
]