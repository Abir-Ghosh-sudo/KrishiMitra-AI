from __future__ import annotations

from celery import Celery
from kombu import Queue

from krishimitra_core.config.settings import get_settings


def create_celery_app() -> Celery:
    """Create and configure the KrishiMitra background worker."""

    settings = get_settings()

    app = Celery(
        "krishimitra_worker",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )

    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,

        task_track_started=True,
        task_send_sent_event=True,

        task_acks_late=True,
        task_reject_on_worker_lost=True,

        worker_prefetch_multiplier=1,

        task_default_queue="default",
        task_queues=(
            Queue("default"),
            Queue("whatsapp"),
            Queue("speech"),
            Queue("vision"),
            Queue("documents"),
            Queue("predictions"),
            Queue("alerts"),
        ),

        task_routes={
            "krishimitra_worker.tasks.whatsapp.*": {
                "queue": "whatsapp",
            },
            "krishimitra_worker.tasks.speech.*": {
                "queue": "speech",
            },
            "krishimitra_worker.tasks.vision.*": {
                "queue": "vision",
            },
            "krishimitra_worker.tasks.documents.*": {
                "queue": "documents",
            },
            "krishimitra_worker.tasks.predictions.*": {
                "queue": "predictions",
            },
            "krishimitra_worker.tasks.alerts.*": {
                "queue": "alerts",
            },
        },

        task_default_retry_delay=5,
        task_max_retries=5,

        broker_connection_retry_on_startup=True,

        worker_send_task_events=True,
    )

    app.autodiscover_tasks(
        packages=[
            "krishimitra_worker.tasks",
        ]
    )

    return app


celery_app = create_celery_app()


__all__ = [
    "celery_app",
    "create_celery_app",
]