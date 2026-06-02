from celery import Celery, signals
from src.settings import init_sentry, settings

celery = Celery(
    backend=None,
    broker=settings.celery_broker_url,
    broker_connection_retry_on_startup=True,
    include=("src.tasks",),
    task_default_queue=settings.celery_task_queue,
    worker_concurrency=1,
    worker_max_tasks_per_child=1,
    worker_prefetch_multiplier=1,
)


@signals.celeryd_init.connect
def initialize_sentry(**kwargs: dict) -> None:
    init_sentry()
