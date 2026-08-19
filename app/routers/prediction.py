"""
DEPRECATED / RETIRED -- 2026-08-11

This router is no longer registered in app/main.py. It duplicated
app/routers/ai_prediction.py with its own standalone RandomForest
trained inline, bypassing the real ensemble pipeline (RF+XGB+LR) in
app/ml/. frontend/src/services/api.js only ever called
/prediction/ai/{ticker}, not this router's /prediction/{ticker}, so
retiring it should be safe -- but confirm before deleting this file
outright.

Kept on disk only so you can diff/reference it. Not imported anywhere.
"""

import asyncio

import pandas as pd
import yfinance as yf

from fastapi import APIRouter, HTTPException
from sklearn.ensemble import RandomForestClassifier

router = APIRouter(
    prefix="/prediction",
    tags=["AI Prediction (DEPRECATED - not registered)"]
)


def normalize_ticker(ticker: str) -> str:
    ticker = ticker.upper()

    if not ticker.startswith("^") and "." not in ticker:
        ticker = ticker + ".NS"

    return ticker


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["return_1d"] = df["Close"].pct_change()
    df["return_5d"] = df["Close"].pct_change(5)

    df["sma20"] = df["Close"].rolling(20).mean()
    df["sma50"] = df["Close"].rolling(50).mean()

    df["price_sma20"] = df["Close"] / df["sma20"] - 1
    df["price_sma50"] = df["Close"] / df["sma50"] - 1

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)

    df["rsi"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = df["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    df["macd"] = ema12 - ema26

    df["macd_signal"] = df["macd"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["volatility_20"] = (
        df["return_1d"].rolling(20).std()
    )

    # Avoid infinity when previous volume is zero.
    previous_volume = df["Volume"].shift(1)

    df["volume_change"] = (
        (df["Volume"] - previous_volume)
        / previous_volume.replace(0, pd.NA)
    )

    df["target"] = (
        df["Close"].shift(-1) > df["Close"]
    ).astype(int)

    # Replace infinity values with missing values.
    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    return df


FEATURES = [
    "return_1d",
    "return_5d",
    "price_sma20",
    "price_sma50",
    "rsi",
    "macd",
    "macd_signal",
    "volatility_20",
    "volume_change"
]


async def download_data(ticker: str):
    return await asyncio.to_thread(
        lambda: yf.Ticker(ticker).history(
            period="5y",
            interval="1d",
            auto_adjust=False
        )
    )


@router.get("/{ticker}")
async def predict_stock(ticker: str):

    ticker = normalize_ticker(ticker)

    try:
        df = await download_data(ticker)

        if df.empty or len(df) < 250:
            raise HTTPException(
                status_code=404,
                detail="Not enough historical data"
            )

        df = build_features(df)

        model_df = df.dropna(
            subset=FEATURES + ["target"]
        ).copy()

        if len(model_df) < 200:
            raise HTTPException(
                status_code=400,
                detail="Not enough usable training data"
            )

        # Time-series split.
        # We do NOT randomly shuffle stock data.
        split = int(len(model_df) * 0.80)

        train = model_df.iloc[:split]
        test = model_df.iloc[split:]

        X_train = train[FEATURES]
        y_train = train["target"]

        X_test = test[FEATURES]
        y_test = test["target"]

        # Final safety check.
        X_train = X_train.astype(float)
        X_test = X_test.astype(float)

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=5,
            random_state=42,
            class_weight="balanced"
        )

        model.fit(
            X_train,
            y_train
        )

        test_accuracy = model.score(
            X_test,
            y_test
        )

        # Latest valid row.
        latest = df.dropna(
            subset=FEATURES
        ).iloc[-1]

        X_latest = latest[
            FEATURES
        ].to_frame().T.astype(float)

        prediction = int(
            model.predict(X_latest)[0]
        )

        probabilities = model.predict_proba(
            X_latest
        )[0]

        down_probability = float(
            probabilities[0]
        )

        up_probability = float(
            probabilities[1]
        )

        if prediction == 1:
            direction = "UP"
            confidence = up_probability
        else:
            direction = "DOWN"
            confidence = down_probability

        if direction == "UP" and confidence >= 0.60:
            signal = "BUY"
        elif direction == "DOWN" and confidence >= 0.60:
            signal = "SELL"
        else:
            signal = "HOLD"

        latest_price = float(
            latest["Close"]
        )

        return {
            "ticker": ticker,
            "source": "Yahoo Finance",

            "prediction": direction,

            "confidence": round(
                confidence * 100,
                2
            ),

            "up_probability": round(
                up_probability * 100,
                2
            ),

            "down_probability": round(
                down_probability * 100,
                2
            ),

            "signal": signal,

            "current_price": round(
                latest_price,
                2
            ),

            "model": "Random Forest",

            "test_accuracy": round(
                test_accuracy * 100,
                2
            ),

            "training_samples": len(train),
            "testing_samples": len(test),

            "indicators": {
                "rsi": round(
                    float(latest["rsi"]),
                    2
                ),

                "macd": round(
                    float(latest["macd"]),
                    2
                ),

                "macd_signal": round(
                    float(latest["macd_signal"]),
                    2
                ),

                "sma20": round(
                    float(latest["sma20"]),
                    2
                ),

                "sma50": round(
                    float(latest["sma50"]),
                    2
                )
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )