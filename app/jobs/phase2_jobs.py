"""
Scheduled market-data synchronization jobs.

These jobs use Yahoo Finance directly and persist data through the
existing application database layer.
"""

import logging

import yfinance as yf

from app.database import query

logger = logging.getLogger(__name__)


def _get_active_stocks():
    """Return all active stocks that have a Yahoo Finance ticker."""
    return query(
        """
        SELECT stock_id, ticker
        FROM stocks
        WHERE active = TRUE
        ORDER BY stock_id
        """,
        fetch=True,
    ) or []


def sync_recent_prices():
    """
    Refresh recent market prices for all active stocks.

    This is intentionally lightweight and is suitable for the
    15-minute scheduler.
    """
    stocks = _get_active_stocks()

    success = 0
    failed = 0

    for stock in stocks:
        ticker = stock["ticker"]

        try:
            data = yf.Ticker(ticker).history(
                period="5d",
                interval="1d",
                auto_adjust=False,
            )

            if data.empty:
                failed += 1
                continue

            for index, row in data.iterrows():
                trade_date = index.date()

                close = row.get("Close")
                open_price = row.get("Open")
                high = row.get("High")
                low = row.get("Low")
                volume = row.get("Volume")

                if close is None:
                    continue

                query(
                    """
                    INSERT INTO stock_prices
                    (
                        stock_id,
                        price_date,
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        volume
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        open_price = VALUES(open_price),
                        high_price = VALUES(high_price),
                        low_price = VALUES(low_price),
                        close_price = VALUES(close_price),
                        volume = VALUES(volume)
                    """,
                    (
                        stock["stock_id"],
                        trade_date,
                        float(open_price) if open_price is not None else None,
                        float(high) if high is not None else None,
                        float(low) if low is not None else None,
                        float(close),
                        int(volume) if volume is not None else None,
                    ),
                )

            success += 1

        except Exception:
            failed += 1
            logger.exception("Recent price sync failed for %s", ticker)

    logger.info(
        "Recent price sync completed: success=%s failed=%s",
        success,
        failed,
    )

    return {
        "success": success,
        "failed": failed,
        "stocks": len(stocks),
    }


def sync_daily_prices():
    """
    Refresh longer daily history for all active stocks.

    Used by the daily scheduler after market close.
    """
    stocks = _get_active_stocks()

    success = 0
    failed = 0

    for stock in stocks:
        ticker = stock["ticker"]

        try:
            data = yf.Ticker(ticker).history(
                period="5y",
                interval="1d",
                auto_adjust=False,
            )

            if data.empty:
                failed += 1
                continue

            for index, row in data.iterrows():
                close = row.get("Close")

                if close is None:
                    continue

                query(
                    """
                    INSERT INTO stock_prices
                    (
                        stock_id,
                        price_date,
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        volume
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        open_price = VALUES(open_price),
                        high_price = VALUES(high_price),
                        low_price = VALUES(low_price),
                        close_price = VALUES(close_price),
                        volume = VALUES(volume)
                    """,
                    (
                        stock["stock_id"],
                        index.date(),
                        float(row["Open"]),
                        float(row["High"]),
                        float(row["Low"]),
                        float(row["Close"]),
                        int(row["Volume"]),
                    ),
                )

            success += 1

        except Exception:
            failed += 1
            logger.exception("Daily price sync failed for %s", ticker)

    logger.info(
        "Daily price sync completed: success=%s failed=%s",
        success,
        failed,
    )

    return {
        "success": success,
        "failed": failed,
        "stocks": len(stocks),
    }


def update_stock_quotes():
    """
    Update the latest quote information for all active stocks.
    """
    stocks = _get_active_stocks()

    success = 0
    failed = 0

    for stock in stocks:
        ticker = stock["ticker"]

        try:
            data = yf.Ticker(ticker).history(
                period="2d",
                interval="1d",
                auto_adjust=False,
            )

            if data.empty:
                failed += 1
                continue

            latest = data.iloc[-1]

            close_price = latest.get("Close")

            if close_price is None:
                failed += 1
                continue

            query(
                """
                UPDATE stocks
                SET
                    last_price = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE stock_id = %s
                """,
                (
                    float(close_price),
                    stock["stock_id"],
                ),
            )

            success += 1

        except Exception:
            failed += 1
            logger.exception("Quote update failed for %s", ticker)

    logger.info(
        "Stock quote update completed: success=%s failed=%s",
        success,
        failed,
    )

    return {
        "success": success,
        "failed": failed,
        "stocks": len(stocks),
    }