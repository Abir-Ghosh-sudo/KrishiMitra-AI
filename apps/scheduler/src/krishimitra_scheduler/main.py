from __future__ import annotations

import logging
import time

from krishimitra_scheduler.jobs.alerts import run_alert_generation
from krishimitra_scheduler.jobs.disease_risk import run_disease_risk_check
from krishimitra_scheduler.jobs.irrigation_check import run_irrigation_check
from krishimitra_scheduler.jobs.model_monitoring import run_model_monitoring
from krishimitra_scheduler.jobs.pest_risk import run_pest_risk_check
from krishimitra_scheduler.jobs.sustainability import run_sustainability_check
from krishimitra_scheduler.jobs.weather_refresh import refresh_weather_data

logger = logging.getLogger(__name__)

DEFAULT_INTERVAL_SECONDS = 60


def run_scheduler_cycle() -> None:
    """Run one scheduler cycle."""

    jobs = (
        refresh_weather_data,
        run_irrigation_check,
        run_disease_risk_check,
        run_pest_risk_check,
        run_sustainability_check,
        run_alert_generation,
        run_model_monitoring,
    )

    for job in jobs:
        try:
            result = job()
            logger.info(
                "Scheduled job completed",
                extra={"job": result.get("job"), "status": result.get("status")},
            )
        except Exception:
            logger.exception(
                "Scheduled job failed",
                extra={"job": job.__name__},
            )


def run_scheduler(
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
) -> None:
    """Run the scheduler continuously."""

    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be greater than zero")

    logger.info(
        "KrishiMitra scheduler started",
        extra={"interval_seconds": interval_seconds},
    )

    while True:
        run_scheduler_cycle()
        time.sleep(interval_seconds)


def main() -> None:
    """Application entrypoint."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    run_scheduler()


if __name__ == "__main__":
    main()