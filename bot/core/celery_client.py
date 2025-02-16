import os
from celery import Celery, schedules
from core.constants import GET_OFFERS_INTERVAL, SEND_OFFERS_INTERVAL

class CeleryClient:
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/3')
    result_backend = os.getenv(
        'CELERY_RESULT_BACKEND', 'redis://localhost:6379/3')
    task_serializer = os.getenv('CELERY_TASK_SERIALIZER', 'json')
    accept_content = os.getenv('CELERY_ACCEPT_CONTENT', 'json').split(',')
    result_serializer = os.getenv('CELERY_RESULT_SERIALIZER', 'json')
    timezone = os.getenv('CELERY_TIMEZONE', 'Europe/Berlin')
    enable_utc = os.getenv('CELERY_ENABLE_UTC',
                           'True').lower() in ('true', '1', 't')

    app = Celery('verschenken_finder', broker=broker_url)

    # Optional configuration settings
    app.conf.update(
        result_backend=result_backend,
        task_serializer=task_serializer,
        accept_content=accept_content,
        result_serializer=result_serializer,
        timezone=timezone,
        enable_utc=enable_utc,
        beat_schedule={
            f'get-offers-every-{GET_OFFERS_INTERVAL}-seconds': {
                'task': 'workers.offers_tasks.get_offers',
                'schedule': schedules.schedule(run_every=GET_OFFERS_INTERVAL),
            },
            f'send-offers-every-{SEND_OFFERS_INTERVAL}-seconds': {
                'task': 'workers.offers_tasks.send_offers_task',
                'schedule': schedules.schedule(run_every=SEND_OFFERS_INTERVAL),
            },
        },
        include=['workers.offers_tasks']
    )
