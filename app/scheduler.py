"""
APScheduler wiring for all sync jobs (Phase 1: app/jobs/sync_jobs.py,
app/jobs/prediction_jobs.py; Phase 2: app/jobs/phase2_jobs.py).

Disabled by default (ENABLE_SCHEDULER unset/false) so merging this file
doesn't suddenly start hammering Yahoo Finance for every stock in your
DB the moment you restart uvicorn. Turn it on deliberately once you've
verified each job works against your actual DB by running it manually
first (see README.md).

Add to .env:
    ENABLE_SCHEDULER=true
"""

import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from app.jobs.sync_jobs import sync_recent_prices, sync_daily_prices, update_stock_quotes
from app.jobs.prediction_jobs import generate_predictions
from app.jobs.phase2_jobs import sync_news, sync_fundamentals, snapshot_market_regime

logger = logging.getLogger("dalal_street.scheduler")
_scheduler = None


def start_scheduler():
    global _scheduler
    if os.getenv("ENABLE_SCHEDULER", "false").lower() != "true":
        logger.info("Scheduler disabled (set ENABLE_SCHEDULER=true in .env to enable)")
        return None

    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

    # Frequent, cheap: keep quotes/prices warm during market hours.
    _scheduler.add_job(sync_recent_prices, "interval", minutes=15, id="sync_recent_prices")
    _scheduler.add_job(update_stock_quotes, "interval", minutes=15, id="update_stock_quotes")

    # Hourly: news is time-sensitive but each fetch is cheap (no ML).
    _scheduler.add_job(sync_news, "interval", hours=1, id="sync_news")

    # A few times a day: cheap heuristic, worth refreshing regularly.
    _scheduler.add_job(snapshot_market_regime, "interval", hours=4, id="snapshot_market_regime")

    # Daily, after market close (IST): expensive/slow jobs.
    _scheduler.add_job(sync_daily_prices, "cron", hour=18, minute=0, id="sync_daily_prices")
    _scheduler.add_job(sync_fundamentals, "cron", hour=19, minute=0, id="sync_fundamentals")
    # Prediction generation is the slowest job (trains 3 models per stock) --
    # runs last, after prices are fresh.
    _scheduler.add_job(generate_predictions, "cron", hour=20, minute=0, id="generate_predictions")

    _scheduler.start()
    logger.info(
        "Scheduler started: prices/quotes every 15min, news hourly, "
        "regime every 4h, daily prices+fundamentals+predictions after 18:00 IST"
    )
    return _scheduler


def shutdown_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
