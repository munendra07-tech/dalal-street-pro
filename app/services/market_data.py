import os
from datetime import datetime

import yfinance as yf

from app.database import query


def normalize_ticker(ticker: str) -> str:
    ticker = ticker.strip().upper()

    # Indian NSE ticker support
    if "." not in ticker and not ticker.startswith("^"):
        ticker = f"{ticker}.NS"

    return ticker


def get_or_create_stock(ticker: str):
    ticker = normalize_ticker(ticker)

    rows = query(
        "SELECT * FROM stocks WHERE ticker = %s",
        (ticker,),
        fetch=True,
    )

    if rows:
        return rows[0]

    name = ticker.replace(".NS", "").replace(".BO", "")

    query(
        """
        INSERT INTO stocks (ticker, name, active)
        VALUES (%s, %s, TRUE)
        """,
        (ticker, name),
    )

    rows = query(
        "SELECT * FROM stocks WHERE ticker = %s",
        (ticker,),
        fetch=True,
    )

    if not rows:
        raise RuntimeError(f"Unable to create stock: {ticker}")

    return rows[0]


def sync_news_for_stock(stock_id: int, ticker: str):
    """
    Placeholder news synchronisation.

    This keeps the intelligence API working while the
    production news provider is integrated.
    """
    return 0


def sync_fundamentals_for_stock(stock_id: int, ticker: str):
    """
    Fetch basic fundamentals from Yahoo Finance and cache them.
    """

    try:
        info = yf.Ticker(ticker).info

        data = {
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "price_to_book": info.get("priceToBook"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "return_on_equity": info.get("returnOnEquity"),
        }

        rows = query(
            "SELECT fundamental_id FROM fundamentals WHERE stock_id = %s",
            (stock_id,),
            fetch=True,
        )

        if rows:
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

    except Exception:
        return False


def detect_market_regime():
    """
    Detect broad NSE market regime using price vs moving averages.
    """

    try:
        df = yf.Ticker("^NSEI").history(
            period="1y",
            auto_adjust=False,
        )

        if df.empty:
            return {
                "regime": "UNKNOWN",
                "confidence": 0,
            }

        close = df["Close"]

        current = float(close.iloc[-1])
        sma20 = float(close.rolling(20).mean().iloc[-1])
        sma50 = float(close.rolling(50).mean().iloc[-1])
        sma200 = float(close.rolling(200).mean().iloc[-1])

        if current > sma20 > sma50 > sma200:
            regime = "BULLISH"
        elif current < sma20 < sma50 < sma200:
            regime = "BEARISH"
        else:
            regime = "SIDEWAYS"

        return {
            "index": "^NSEI",
            "current": round(current, 2),
            "sma20": round(sma20, 2),
            "sma50": round(sma50, 2),
            "sma200": round(sma200, 2),
            "regime": regime,
        }

    except Exception as e:
        return {
            "regime": "UNKNOWN",
            "error": str(e),
        }