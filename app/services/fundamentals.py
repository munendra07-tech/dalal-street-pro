import math

import yfinance as yf

from app.database import query


def _clean(value):
    """Convert NaN/infinite values to None for MySQL."""
    if value is None:
        return None

    try:
        value = float(value)

        if not math.isfinite(value):
            return None

        return value
    except (TypeError, ValueError):
        return None


def sync_fundamentals_for_stock(stock_id: int, ticker: str) -> bool:
    """
    Fetch fundamental data from Yahoo Finance and cache it
    in the fundamentals table.
    """

    try:
        info = yf.Ticker(ticker).info

        data = {
            "market_cap": _clean(info.get("marketCap")),
            "pe_ratio": _clean(info.get("trailingPE")),
            "forward_pe": _clean(info.get("forwardPE")),
            "price_to_book": _clean(info.get("priceToBook")),
            "eps": _clean(info.get("trailingEps")),
            "dividend_yield": _clean(info.get("dividendYield")),
            "profit_margin": _clean(info.get("profitMargins")),
            "revenue_growth": _clean(info.get("revenueGrowth")),
            "return_on_equity": _clean(info.get("returnOnEquity")),
        }

        existing = query(
            """
            SELECT fundamental_id
            FROM fundamentals
            WHERE stock_id = %s
            LIMIT 1
            """,
            (stock_id,),
            fetch=True,
        )

        if existing:
            query(
                """
                UPDATE fundamentals
                SET market_cap=%s,
                    pe_ratio=%s,
                    forward_pe=%s,
                    price_to_book=%s,
                    eps=%s,
                    dividend_yield=%s,
                    profit_margin=%s,
                    revenue_growth=%s,
                    return_on_equity=%s
                WHERE stock_id=%s
                """,
                (
                    data["market_cap"],
                    data["pe_ratio"],
                    data["forward_pe"],
                    data["price_to_book"],
                    data["eps"],
                    data["dividend_yield"],
                    data["profit_margin"],
                    data["revenue_growth"],
                    data["return_on_equity"],
                    stock_id,
                ),
            )
        else:
            query(
                """
                INSERT INTO fundamentals
                (
                    stock_id,
                    market_cap,
                    pe_ratio,
                    forward_pe,
                    price_to_book,
                    eps,
                    dividend_yield,
                    profit_margin,
                    revenue_growth,
                    return_on_equity
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    stock_id,
                    data["market_cap"],
                    data["pe_ratio"],
                    data["forward_pe"],
                    data["price_to_book"],
                    data["eps"],
                    data["dividend_yield"],
                    data["profit_margin"],
                    data["revenue_growth"],
                    data["return_on_equity"],
                ),
            )

        return True

    except Exception as exc:
        print(f"Fundamentals sync failed for {ticker}: {exc}")
        return False