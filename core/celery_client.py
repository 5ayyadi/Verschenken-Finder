import os
from celery import Celery, schedules
from core.mongo_client import MongoDBClient
from core.constants import (
    GET_OFFERS_INTERVAL,
    SEND_OFFERS_INTERVAL,
    GET_OFFERS_TASK,
    SEND_OFFERS_TASK,
)

class CeleryClient:
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/3')
    result_backend = os.getenv(
        'CELERY_RESULT_BACKEND', 'redis://redis:6379/3')
    task_serializer = os.getenv('CELERY_TASK_SERIALIZER', 'json')
    accept_content = os.getenv('CELERY_ACCEPT_CONTENT', 'json').split(',')
    result_serializer = os.getenv('CELERY_RESULT_SERIALIZER', 'json')
    timezone = os.getenv('CELERY_TIMEZONE', 'Europe/Berlin')
    enable_utc = os.getenv('CELERY_ENABLE_UTC',
                           'True').lower() in ('true', '1', 't')

    app = Celery('verschenken_finder', broker=broker_url)

    app.conf.update(
        result_backend=result_backend,
        task_serializer=task_serializer,
        accept_content=accept_content,
        result_serializer=result_serializer,
        timezone=timezone,
        enable_utc=enable_utc,
        beat_schedule={
            f'get-offers-every-{GET_OFFERS_INTERVAL}-seconds': {
                'task': GET_OFFERS_TASK,
                'schedule': schedules.schedule(run_every=GET_OFFERS_INTERVAL),
            },
            f'send-offers-every-{SEND_OFFERS_INTERVAL}-seconds': {
                'task': SEND_OFFERS_TASK,
                'schedule': schedules.schedule(run_every=SEND_OFFERS_INTERVAL),
            },
        },
        include=['workers.offers_tasks']
    )
    
    @classmethod
    def get_app(cls):
        return cls.app

app = CeleryClient.get_app()

# Initialize MongoDB for Celery workers
@app.on_after_configure.connect
def setup_mongodb(sender, **kwargs):
    # Initialize MongoDB client
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    MongoDBClient.initialize(mongo_uri)