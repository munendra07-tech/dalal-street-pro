"""
News, sentiment, fundamentals, and market regime endpoints.
Grouped in one router file since each is a thin read/trigger wrapper
around app/services/{news,fundamentals,market_regime}.py.
"""

from fastapi import APIRouter, HTTPException
from app.database import query
from app.services.market_data import normalize_ticker, get_or_create_stock
from app.services.news import sync_news_for_stock
from app.services.fundamentals import sync_fundamentals_for_stock
from app.services.market_regime import detect_market_regime

router = APIRouter(tags=["Market Intelligence"])


def _resolve_stock(ticker: str):
    ticker = normalize_ticker(ticker)
    rows = query("SELECT stock_id, ticker, company FROM stocks WHERE ticker = %s", (ticker,), fetch=True)
    if rows:
        return rows[0]
    # Not in our universe yet -- create a minimal row so news/fundamentals
    # can still be looked up on demand rather than hard-failing.
    stock_id = get_or_create_stock(ticker)
    return {"stock_id": stock_id, "ticker": ticker, "company": ticker}


@router.get("/news/{ticker}")
def get_news(ticker: str, refresh: bool = False):
    stock = _resolve_stock(ticker)

    if refresh:
        try:
            sync_news_for_stock(stock["stock_id"], stock["ticker"])
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"News fetch failed: {e}")

    rows = query(
        """
        SELECT headline, source, url, published_at, sentiment_label, sentiment_score
        FROM market_news WHERE stock_id = %s
        ORDER BY published_at DESC LIMIT 20
        """,
        (stock["stock_id"],), fetch=True,
    )
    if not rows and not refresh:
        return {"ticker": stock["ticker"], "news": [], "note": "No cached news. Call with ?refresh=true to fetch now."}
    return {"ticker": stock["ticker"], "news": rows}


@router.get("/sentiment/{ticker}")
def get_sentiment(ticker: str):
    stock = _resolve_stock(ticker)
    rows = query(
        "SELECT sentiment_label, sentiment_score FROM market_news WHERE stock_id=%s AND sentiment_label IS NOT NULL",
        (stock["stock_id"],), fetch=True,
    )
    if not rows:
        return {"ticker": stock["ticker"], "sentiment": None, "note": "No scored news available yet."}

    counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
    for r in rows:
        counts[r["sentiment_label"]] = counts.get(r["sentiment_label"], 0) + 1
    avg_score = round(sum(float(r["sentiment_score"]) for r in rows if r["sentiment_score"] is not None) / len(rows), 2)
    overall = max(counts, key=counts.get)

    return {
        "ticker": stock["ticker"],
        "overall_sentiment": overall,
        "avg_score": avg_score,
        "article_counts": counts,
        "based_on_articles": len(rows),
    }


@router.get("/fundamentals/{ticker}")
def get_fundamentals(ticker: str, refresh: bool = False):
    stock = _resolve_stock(ticker)

    if refresh:
        ok = sync_fundamentals_for_stock(stock["stock_id"], stock["ticker"])
        if not ok:
            raise HTTPException(status_code=502, detail="Fundamentals fetch failed")

    rows = query("SELECT * FROM fundamentals WHERE stock_id = %s", (stock["stock_id"],), fetch=True)
    if not rows:
        return {"ticker": stock["ticker"], "fundamentals": None, "note": "No cached fundamentals. Call with ?refresh=true to fetch now."}
    return {"ticker": stock["ticker"], "fundamentals": rows[0]}


@router.get("/analytics/regime")
def market_regime():
    return detect_market_regime()
