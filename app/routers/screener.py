"""
AI Stock Screener (spec section 20).

Deliberately does NOT call the live ensemble-training pipeline per
request -- that would mean training 3 models per stock for every
screener page load, which is exactly what spec section 49 says not to
do. Instead:

  - AI score comes from the `predictions` table, populated by the
    nightly app.jobs.prediction_jobs.generate_predictions() batch job.
  - Technical score is computed cheaply from stored price_history
    (no ML, no external calls) so it's always fresh.

If a stock has no cached prediction yet (job hasn't run, or stock was
just added), its AI component is reported as unavailable rather than
faked -- per spec section 46 ("real data policy").
"""

from fastapi import APIRouter, Query
from app.database import query

router = APIRouter(prefix="/screener", tags=["AI Screener"])


def _technical_score_sql():
    """
    Cheap technical score (0-100) computed directly in SQL from the last
    ~20 rows of price_history per stock: trend vs SMA20, RSI proxy via
    recent up/down day ratio, and volume vs its own recent average.
    This intentionally mirrors the spirit of the 19-feature ML pipeline
    without re-running it -- it's a fast heuristic for ranking, not a
    replacement for the AI score.
    """
    return """
        WITH recent AS (
            SELECT ph.stock_id, ph.close_price, ph.volume, ph.recorded_at,
                   ROW_NUMBER() OVER (PARTITION BY ph.stock_id ORDER BY ph.recorded_at DESC) AS rn
            FROM price_history ph
        ),
        last20 AS (
            SELECT stock_id, close_price, volume, recorded_at, rn FROM recent WHERE rn <= 20
        ),
        agg AS (
            SELECT
                stock_id,
                MAX(CASE WHEN rn = 1 THEN close_price END) AS latest_close,
                AVG(close_price) AS sma20,
                AVG(volume) AS avg_vol20,
                MAX(CASE WHEN rn = 1 THEN volume END) AS latest_vol,
                COUNT(*) AS n_rows,
                SUM(CASE WHEN rn <= 10 THEN close_price ELSE 0 END) / NULLIF(SUM(CASE WHEN rn <= 10 THEN 1 ELSE 0 END), 0) AS sma10
            FROM last20
            GROUP BY stock_id
        )
        SELECT
            stock_id, latest_close, sma20, sma10, avg_vol20, latest_vol, n_rows,
            CASE WHEN n_rows >= 10 THEN
                LEAST(100, GREATEST(0,
                    50
                    + ((latest_close - sma20) / NULLIF(sma20, 0)) * 300   -- trend vs SMA20
                    + ((sma10 - sma20) / NULLIF(sma20, 0)) * 200          -- short vs long trend
                    + LEAST(GREATEST((latest_vol - avg_vol20) / NULLIF(avg_vol20, 0), -1), 1) * 10
                ))
            ELSE NULL END AS technical_score
        FROM agg
    """


@router.get("/top")
def top_opportunities(limit: int = Query(20, le=100), min_confidence: float = Query(0, ge=0, le=100)):
    """
    TOP AI OPPORTUNITIES (spec sections 20 + 24) -- transparent composite
    of up to four independently-available components:
      - AI score: latest cached ensemble prediction's up_probability
      - Technical score: cheap SQL heuristic (see _technical_score_sql)
      - Fundamental score: from services/fundamentals.py, if cached
      - Sentiment score: avg news sentiment, if any scored articles exist

    Weights (when all four available): AI 35%, Technical 25%,
    Fundamental 25%, Sentiment 15%. Missing components are dropped and
    the remaining weights renormalized -- never padded with a guess.
    `data_available` on each row always shows exactly which components
    contributed, so this is auditable, not a black box.
    """
    WEIGHTS = {"ai": 0.35, "technical": 0.25, "fundamental": 0.25, "sentiment": 0.15}

    tech_rows = query(_technical_score_sql(), fetch=True)
    tech_by_stock = {r["stock_id"]: r for r in tech_rows}

    pred_rows = query(
        """
        SELECT p.stock_id, p.prediction, p.confidence, p.up_probability,
               p.down_probability, p.signal, p.prediction_date
        FROM predictions p
        INNER JOIN (
            SELECT stock_id, MAX(prediction_date) AS max_date
            FROM predictions WHERE model = 'ensemble' GROUP BY stock_id
        ) latest ON p.stock_id = latest.stock_id AND p.prediction_date = latest.max_date
        WHERE p.model = 'ensemble'
        """,
        fetch=True,
    )
    pred_by_stock = {r["stock_id"]: r for r in pred_rows}

    fund_rows = query(
        "SELECT stock_id, fundamental_score FROM fundamentals WHERE fundamental_score IS NOT NULL",
        fetch=True,
    )
    fund_by_stock = {r["stock_id"]: float(r["fundamental_score"]) for r in fund_rows}

    sentiment_rows = query(
        """
        SELECT stock_id, AVG(sentiment_score) AS avg_sentiment, COUNT(*) AS n
        FROM market_news WHERE sentiment_score IS NOT NULL
        GROUP BY stock_id HAVING n >= 2
        """,
        fetch=True,
    )
    sentiment_by_stock = {r["stock_id"]: float(r["avg_sentiment"]) for r in sentiment_rows}

    stocks = query(
        "SELECT stock_id, ticker, company, sector, current_price, prev_close FROM stocks WHERE active = TRUE",
        fetch=True,
    )

    results = []
    for s in stocks:
        sid = s["stock_id"]
        pred = pred_by_stock.get(sid)
        tech = tech_by_stock.get(sid)
        tech_score = float(tech["technical_score"]) if tech and tech["technical_score"] is not None else None
        ai_score = float(pred["up_probability"]) if pred else None
        fund_score = fund_by_stock.get(sid)
        sent_score = sentiment_by_stock.get(sid)

        if pred and pred["confidence"] is not None and float(pred["confidence"]) < min_confidence:
            continue

        components = {"ai": ai_score, "technical": tech_score, "fundamental": fund_score, "sentiment": sent_score}
        available = {k: v for k, v in components.items() if v is not None}
        if not available:
            continue  # nothing to score this stock on at all -- skip, don't fabricate

        weight_sum = sum(WEIGHTS[k] for k in available)
        composite = round(sum(WEIGHTS[k] * v for k, v in available.items()) / weight_sum, 1)

        results.append({
            "ticker": s["ticker"],
            "company": s["company"],
            "sector": s["sector"],
            "current_price": float(s["current_price"]) if s["current_price"] else None,
            "composite_score": composite,
            "ai_prediction": pred["prediction"] if pred else None,
            "ai_confidence": float(pred["confidence"]) if pred else None,
            "ai_signal": pred["signal"] if pred else None,
            "ai_prediction_date": str(pred["prediction_date"]) if pred else None,
            "technical_score": round(tech_score, 1) if tech_score is not None else None,
            "fundamental_score": round(fund_score, 1) if fund_score is not None else None,
            "sentiment_score": round(sent_score, 1) if sent_score is not None else None,
            "data_available": {k: (v is not None) for k, v in components.items()},
        })

    results.sort(key=lambda r: r["composite_score"], reverse=True)
    return results[:limit]


@router.get("/unusual-volume")
def unusual_volume(limit: int = Query(20, le=100)):
    """Section 30: stocks trading well above their 20-day average volume today."""
    tech_rows = query(_technical_score_sql(), fetch=True)
    out = []
    for r in tech_rows:
        if not r["avg_vol20"] or not r["latest_vol"]:
            continue
        ratio = float(r["latest_vol"]) / float(r["avg_vol20"]) if float(r["avg_vol20"]) > 0 else 0
        if ratio >= 1.5:
            out.append({"stock_id": r["stock_id"], "volume_ratio": round(ratio, 2)})
    out.sort(key=lambda r: r["volume_ratio"], reverse=True)
    if not out:
        return []
    ids = [o["stock_id"] for o in out[:limit]]
    placeholders = ",".join(["%s"] * len(ids))
    stocks = {
        s["stock_id"]: s for s in query(
            f"SELECT stock_id, ticker, company, sector FROM stocks WHERE stock_id IN ({placeholders})",
            tuple(ids), fetch=True,
        )
    }
    return [
        {**stocks[o["stock_id"]], "volume_ratio": o["volume_ratio"]}
        for o in out[:limit] if o["stock_id"] in stocks
    ]
