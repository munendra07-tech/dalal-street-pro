import asyncio
import yfinance as yf
import pandas as pd

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/live", tags=["Live Prices"])


def normalize_ticker(ticker: str) -> str:
    ticker = ticker.upper()

    if not ticker.startswith("^") and "." not in ticker:
        ticker = ticker + ".NS"

    return ticker


@router.get("/test")
async def test_live():
    return {"status": "working"}


@router.get("/{ticker}")
async def live_quote(ticker: str):
    ticker = normalize_ticker(ticker)

    try:
        stock = yf.Ticker(ticker)

        df = await asyncio.to_thread(
            lambda: stock.history(
                period="5d",
                interval="1d",
                auto_adjust=False
            )
        )

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {ticker}"
            )

        latest = df.iloc[-1]
        price = float(latest["Close"])

        if len(df) >= 2:
            previous = float(df.iloc[-2]["Close"])
            change = price - previous
            change_pct = (change / previous) * 100
        else:
            change = 0
            change_pct = 0

        return {
            "ticker": ticker,
            "price": price,
            "open": float(latest["Open"]),
            "high": float(latest["High"]),
            "low": float(latest["Low"]),
            "volume": int(latest["Volume"]),
            "change": round(change, 2),
            "change_pct": f"{change_pct:.2f}",
            "date": df.index[-1].strftime("%Y-%m-%d"),
            "source": "Yahoo Finance"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{ticker}/history")
async def price_history(ticker: str, period: str = "1y"):
    ticker = normalize_ticker(ticker)

    allowed_periods = [
        "5d", "1mo", "3mo", "6mo", "1y",
        "2y", "5y", "10y", "max"
    ]

    if period not in allowed_periods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period: {period}"
        )

    try:
        stock = yf.Ticker(ticker)

        df = await asyncio.to_thread(
            lambda: stock.history(
                period=period,
                interval="1d",
                auto_adjust=False
            )
        )

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for {ticker}"
            )

        # Moving averages
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["SMA200"] = df["Close"].rolling(200).mean()

        # RSI
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df["Close"].ewm(
            span=12,
            adjust=False
        ).mean()

        ema26 = df["Close"].ewm(
            span=26,
            adjust=False
        ).mean()

        df["MACD"] = ema12 - ema26

        df["MACD_signal"] = df["MACD"].ewm(
            span=9,
            adjust=False
        ).mean()

        # Bollinger Bands
        df["BB_middle"] = df["Close"].rolling(20).mean()

        std20 = df["Close"].rolling(20).std()

        df["BB_upper"] = df["BB_middle"] + (2 * std20)
        df["BB_lower"] = df["BB_middle"] - (2 * std20)

        # Volume average
        df["Volume_avg20"] = df["Volume"].rolling(20).mean()

        df = df.reset_index()

        data = []

        for _, row in df.iterrows():

            def val(column):
                value = row[column]

                if pd.isna(value):
                    return None

                return round(float(value), 2)

            data.append({
                "date": row["Date"].strftime("%Y-%m-%d"),
                "open": val("Open"),
                "high": val("High"),
                "low": val("Low"),
                "close": val("Close"),
                "volume": int(row["Volume"]),
                "sma20": val("SMA20"),
                "sma50": val("SMA50"),
                "sma200": val("SMA200"),
                "rsi": val("RSI"),
                "macd": val("MACD"),
                "macd_signal": val("MACD_signal"),
                "bb_upper": val("BB_upper"),
                "bb_middle": val("BB_middle"),
                "bb_lower": val("BB_lower"),
                "volume_avg20": val("Volume_avg20")
            })

        latest = df.iloc[-1]

        def latest_val(column):
            value = latest[column]

            if pd.isna(value):
                return None

            return round(float(value), 2)

        current_price = float(latest["Close"])

        if (
            pd.notna(latest["SMA50"])
            and current_price > latest["SMA50"]
        ):
            trend = "BULLISH"
        elif (
            pd.notna(latest["SMA50"])
            and current_price < latest["SMA50"]
        ):
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"

        summary = {
            "price": round(current_price, 2),
            "sma20": latest_val("SMA20"),
            "sma50": latest_val("SMA50"),
            "sma200": latest_val("SMA200"),
            "rsi": latest_val("RSI"),
            "macd": latest_val("MACD"),
            "macd_signal": latest_val("MACD_signal"),
            "bb_upper": latest_val("BB_upper"),
            "bb_middle": latest_val("BB_middle"),
            "bb_lower": latest_val("BB_lower"),
            "trend": trend
        }

        return {
            "ticker": ticker,
            "period": period,
            "source": "Yahoo Finance",
            "count": len(data),
            "summary": summary,
            "data": data
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Historical data error: {str(e)}"
        )
