import os
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.jobs.phase2_jobs import (
    sync_recent_prices,
    sync_daily_prices,
    update_stock_quotes,
)
from app.services.market_regime import snapshot_market_regime

logger = logging.getLogger("dalal_street.scheduler")

_scheduler = None


def start_scheduler():
    global _scheduler

    if os.getenv("ENABLE_SCHEDULER", "false").lower() != "true":
        logger.info(
            "Scheduler disabled (set ENABLE_SCHEDULER=true in .env to enable)"
        )
        return None

    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

    # Every 15 minutes
    _scheduler.add_job(
        sync_recent_prices,
        "interval",
        minutes=15,
        id="sync_recent_prices",
    )

    _scheduler.add_job(
        update_stock_quotes,
        "interval",
        minutes=15,
        id="update_stock_quotes",
    )

    # Every 4 hours
    _scheduler.add_job(
        snapshot_market_regime,
        "interval",
        hours=4,
        id="snapshot_market_regime",
    )

    # Daily after market close
    _scheduler.add_job(
        sync_daily_prices,
        "cron",
        hour=18,
        minute=0,
        id="sync_daily_prices",
    )

    _scheduler.start()

    logger.info(
        "Scheduler started: prices/quotes every 15min, "
        "market regime every 4h, daily prices at 18:00 IST"
    )

    return _scheduler


def shutdown_scheduler():
    global _scheduler

    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
