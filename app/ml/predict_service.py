"""
Reusable AI prediction pipeline. Extracted out of routers/ai_prediction.py
so both the on-demand endpoint AND the batch job (app/jobs/prediction_jobs.py)
call the exact same code path -- no drift between what a user sees live vs.
what gets stored for the screener.

This does NOT change behaviour of the existing /prediction/ai/{ticker}
endpoint -- it's the same logic, just moved so it's callable from
elsewhere too (spec section 49: separate training from prediction from
the API layer).
"""

import logging
import yfinance as yf

from app.ml.features import prepare_training_data
from app.ml.ensemble import ensemble_prediction
from app.ml.explain import generate_explanation
from app.ml.risk import calculate_risk

logger = logging.getLogger("dalal_street.predict_service")

MIN_TRAINING_ROWS = 700


class PredictionError(Exception):
    """Raised when a prediction can't be produced (bad ticker, insufficient data, etc.)."""


def run_ai_prediction(ticker: str, period: str = "5y") -> dict:
    """
    Full pipeline: fetch -> feature engineer -> train ensemble on all but
    the latest row -> predict the latest row -> explain -> risk.

    Raises PredictionError with a human-readable message on any failure
    (unknown ticker, not enough history, etc.) so callers (router or
    batch job) can decide how to handle it without inspecting exception
    internals.
    """
    ticker = ticker.upper()

    df = yf.Ticker(ticker).history(period=period, auto_adjust=False)
    if df is None or df.empty:
        raise PredictionError(f"No market data found for {ticker}")

    X, y, clean_df = prepare_training_data(df)
    if len(X) < MIN_TRAINING_ROWS:
        raise PredictionError(
            f"Not enough historical data for AI prediction "
            f"({len(X)} rows, need {MIN_TRAINING_ROWS})"
        )

    X_train, y_train = X.iloc[:-1], y.iloc[:-1]
    X_current = X.iloc[[-1]]

    prediction = ensemble_prediction(X_train, y_train, X_current)

    latest = clean_df.iloc[-1]
    current_price = float(latest["Close"])

    indicators = {
        "current_price": current_price,
        "rsi": float(latest["rsi"]),
        "macd": float(latest["macd"]),
        "macd_signal": float(latest["macd_signal"]),
        "sma20": float(latest["sma20"]),
        "sma50": float(latest["sma50"]),
        "sma200": float(latest["sma200"]),
        "volatility_20": float(latest["volatility_20"]),
        "atr": float(latest["atr"]),
    }

    risk = calculate_risk(indicators)
    explanation = generate_explanation(prediction, indicators, prediction["model_probabilities"])

    return {
        "ticker": ticker,
        "source": "Yahoo Finance",
        "current_price": round(current_price, 2),
        "prediction": prediction["direction"],
        "signal": prediction["signal"],
        "confidence": prediction["confidence"],
        "up_probability": prediction["up_probability"],
        "down_probability": prediction["down_probability"],
        "models": prediction["model_probabilities"],
        "model_predictions": prediction["model_predictions"],
        "risk": risk,
        "indicators": {k: round(v, 4) for k, v in indicators.items()},
        "explanation": explanation,
        "training_samples": len(X_train),
    }
