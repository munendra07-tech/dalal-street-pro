"""
Data Health dashboard (spec section 39). Every number here is a real
COUNT/MAX from the DB -- if a sync job has never run, the response says
so explicitly rather than showing a plausible-looking zero.
"""

from fastapi import APIRouter
from app.database import query

router = APIRouter(prefix="/admin/data-health", tags=["Data Health"])


@router.get("/")
def data_health():
    stocks_total = query("SELECT COUNT(*) AS n FROM stocks WHERE active = TRUE", fetch=True)[0]["n"]

    updated_today = query(
        "SELECT COUNT(*) AS n FROM stocks WHERE active = TRUE AND DATE(updated_at) = CURDATE()",
        fetch=True,
    )[0]["n"]

    stale = stocks_total - updated_today

    recent_jobs = query(
        """
        SELECT job_name, started_at, completed_at, status, records_processed, records_failed
        FROM data_sync_log
        WHERE sync_id IN (
            SELECT MAX(sync_id) FROM data_sync_log GROUP BY job_name
        )
        ORDER BY started_at DESC
        """,
        fetch=True,
    )

    last_sync = query(
        "SELECT MAX(completed_at) AS latest FROM data_sync_log WHERE status IN ('SUCCESS','PARTIAL')",
        fetch=True,
    )[0]["latest"]

    failed_last_24h = query(
        """
        SELECT job_name, COUNT(*) AS failures, SUM(records_failed) AS total_records_failed
        FROM data_sync_log
        WHERE started_at >= NOW() - INTERVAL 24 HOUR AND status IN ('FAILED','PARTIAL')
        GROUP BY job_name
        """,
        fetch=True,
    )

    price_coverage = query(
        """
        SELECT COUNT(DISTINCT stock_id) AS stocks_with_history
        FROM price_history
        """,
        fetch=True,
    )[0]["stocks_with_history"]

    prediction_coverage = query(
        """
        SELECT COUNT(DISTINCT stock_id) AS stocks_with_predictions
        FROM predictions WHERE prediction_date = CURDATE()
        """,
        fetch=True,
    )[0]["stocks_with_predictions"]

    return {
        "stocks_tracked": stocks_total,
        "stocks_updated_today": updated_today,
        "stocks_stale": stale,
        "stocks_with_price_history": price_coverage,
        "stocks_with_todays_prediction": prediction_coverage,
        "latest_successful_sync": str(last_sync) if last_sync else None,
        "recent_jobs": recent_jobs,
        "failures_last_24h": failed_last_24h,
    }
