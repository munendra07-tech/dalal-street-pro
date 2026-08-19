"""
AI Research Assistant (spec section 34).

IMPORTANT DESIGN NOTE: this does NOT call an LLM. There's no
ANTHROPIC_API_KEY (or similar) configured anywhere in this project, and
wiring one in is a real architectural decision (cost, latency, a new
secret to manage) that you should make deliberately, not have made for
you as a side effect of a "research assistant" feature.

Instead, this is a small rule-based intent parser: it recognizes
patterns like "analyze X", "compare X and Y", "<sector> stocks with
momentum", "portfolio risk", "high volume stocks" -- and routes each to
the SAME functions the rest of the app already uses (predict_service,
screener, analytics, risk). Every number in a response traces back to a
real DB query or a real model run. If the query doesn't match a known
pattern, it says so and lists what it can do, rather than guessing.

If you later add a real LLM, the clean integration point is: keep this
rule-based router as a fast-path / fallback, and let the LLM call these
same underlying functions as tools (function-calling) rather than
letting it free-generate market commentary -- that's what keeps
"do not hallucinate market prices" (spec section 34) actually true.
"""

import re
from fastapi import APIRouter, Query
from app.database import query
from app.services.market_data import normalize_ticker
from app.ml.predict_service import run_ai_prediction, PredictionError

router = APIRouter(prefix="/research", tags=["AI Research Assistant"])

_TICKER_PATTERN = re.compile(r"\b([A-Za-z]{2,15}(?:\.NS|\.BO)?)\b")

_KNOWN_SECTORS = None  # lazily loaded from DB


def _load_known_sectors():
    global _KNOWN_SECTORS
    if _KNOWN_SECTORS is None:
        rows = query("SELECT DISTINCT sector FROM stocks WHERE sector IS NOT NULL", fetch=True)
        _KNOWN_SECTORS = {r["sector"].upper(): r["sector"] for r in rows}
    return _KNOWN_SECTORS


def _extract_tickers(text: str) -> list[str]:
    """Match against real tickers in the DB rather than accepting any capitalized word."""
    candidates = {normalize_ticker(t) for t in _TICKER_PATTERN.findall(text.upper())}
    if not candidates:
        return []
    placeholders = ",".join(["%s"] * len(candidates))
    rows = query(
        f"SELECT ticker FROM stocks WHERE ticker IN ({placeholders})",
        tuple(candidates), fetch=True,
    )
    return [r["ticker"] for r in rows]


def _handle_analyze(ticker: str) -> dict:
    try:
        pred = run_ai_prediction(ticker)
    except PredictionError as e:
        return {"intent": "analyze", "ticker": ticker, "error": str(e)}

    return {
        "intent": "analyze",
        "ticker": ticker,
        "answer": (
            f"{ticker} is trading at ₹{pred['current_price']}. The AI ensemble predicts "
            f"{pred['prediction']} with {pred['confidence']}% confidence (signal: {pred['signal']}). "
            f"RSI is {pred['indicators']['rsi']}, price vs SMA50 suggests "
            f"{'above' if pred['current_price'] > pred['indicators']['sma50'] else 'below'} the 50-day trend. "
            f"Risk category: {pred['risk'].get('risk_category', 'N/A')}."
        ),
        "data": pred,
    }


def _handle_compare(tickers: list[str]) -> dict:
    results = {}
    for t in tickers[:5]:
        try:
            results[t] = run_ai_prediction(t)
        except PredictionError as e:
            results[t] = {"error": str(e)}
    return {"intent": "compare", "tickers": tickers[:5], "data": results}


def _handle_sector_momentum(sector: str) -> dict:
    rows = query(
        """
        SELECT ticker, company,
               ROUND((current_price-prev_close)/NULLIF(prev_close,0)*100,2) AS change_pct
        FROM stocks WHERE sector = %s AND active=TRUE AND prev_close > 0
        ORDER BY change_pct DESC LIMIT 10
        """,
        (sector,), fetch=True,
    )
    return {
        "intent": "sector_momentum",
        "sector": sector,
        "answer": f"Top {sector} stocks by today's momentum, based on stored price data:",
        "data": rows,
    }


def _handle_unusual_volume() -> dict:
    from app.routers.screener import unusual_volume
    return {"intent": "unusual_volume", "data": unusual_volume()}


def _handle_portfolio_risk(portfolio_id: int) -> dict:
    rows = query("SELECT * FROM v_portfolio_pnl WHERE portfolio_id=%s", (portfolio_id,), fetch=True)
    if not rows:
        return {"intent": "portfolio_risk", "error": "No holdings found for this portfolio."}
    total_value = sum(float(r["current_value"] or 0) for r in rows)
    by_sector = {}
    for r in rows:
        sector = r["sector"] or "Unknown"
        by_sector[sector] = by_sector.get(sector, 0) + float(r["current_value"] or 0)
    largest_sector, largest_val = max(by_sector.items(), key=lambda kv: kv[1]) if by_sector else (None, 0)
    concentration_pct = round(largest_val / total_value * 100, 1) if total_value else 0
    return {
        "intent": "portfolio_risk",
        "answer": (
            f"Portfolio holds {len(rows)} stocks worth ₹{total_value:,.2f}. "
            f"Largest sector exposure: {largest_sector} at {concentration_pct}% of holdings."
            + (" This is a concentrated position -- consider diversifying." if concentration_pct > 40 else "")
        ),
        "sector_allocation": {k: round(v / total_value * 100, 1) if total_value else 0 for k, v in by_sector.items()},
    }


@router.get("/ask")
def ask(q: str = Query(..., min_length=2), portfolio_id: int = None):
    """
    Natural-language-ish research queries, routed by pattern matching
    against real endpoints. Examples the spec calls out: "Analyze
    Reliance.", "Compare Reliance and TCS.", "Which banking stocks have
    strong momentum?", "Show high-volume stocks.", "Analyze my
    portfolio risk."
    """
    text = q.strip()
    lower = text.lower()
    tickers = _extract_tickers(text)
    sectors = _load_known_sectors()

    if "portfolio" in lower and "risk" in lower:
        if not portfolio_id:
            return {"intent": "portfolio_risk", "error": "Pass ?portfolio_id=<id> to analyze a specific portfolio."}
        return _handle_portfolio_risk(portfolio_id)

    if "volume" in lower and ("high" in lower or "unusual" in lower):
        return _handle_unusual_volume()

    if ("compare" in lower or " vs " in lower or " and " in lower) and len(tickers) >= 2:
        return _handle_compare(tickers)

    for sector_upper, sector_display in sectors.items():
        if sector_upper.lower() in lower:
            return _handle_sector_momentum(sector_display)

    if tickers:
        return _handle_analyze(tickers[0])

    return {
        "intent": "unknown",
        "answer": (
            "I couldn't match that to a known stock, sector, or request type. "
            "Try: 'Analyze RELIANCE', 'Compare TCS and INFY', "
            "'<sector name> stocks with momentum' (e.g. 'Banking stocks with strong momentum'), "
            "'Show high-volume stocks', or 'Analyze my portfolio risk' (with ?portfolio_id=)."
        ),
    }
