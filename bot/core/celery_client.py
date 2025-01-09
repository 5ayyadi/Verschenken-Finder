import os
from celery import Celery

class CeleryClient:
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    task_serializer = os.getenv('CELERY_TASK_SERIALIZER', 'json')
    accept_content = os.getenv('CELERY_ACCEPT_CONTENT', 'json').split(',')
    result_serializer = os.getenv('CELERY_RESULT_SERIALIZER', 'json')
    timezone = os.getenv('CELERY_TIMEZONE', 'Europe/Berlin')
    enable_utc = os.getenv('CELERY_ENABLE_UTC', 'True').lower() in ('true', '1', 't')

    app = Celery('verschenken_finder', broker=broker_url)

    # Optional configuration settings
    app.conf.update(
        result_backend=result_backend,
        task_serializer=task_serializer,
        accept_content=accept_content,
        result_serializer=result_serializer,
        timezone=timezone,
        enable_utc=enable_utc,
    )

    @classmethod
    async def start_celery(cls):
        """Start the Celery worker."""
        cls.app.start()

    @classmethod
    async def stop_celery(cls):
        """Stop the Celery worker."""
        # Implement the logic to stop the Celery worker if needed
        cls.app.control.shutdown()
    