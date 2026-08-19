import yfinance as yf


def detect_market_regime():
    """
    Detect the current broad Indian market regime using NIFTY 50.
    """

    try:
        df = yf.Ticker("^NSEI").history(
            period="1y",
            auto_adjust=False,
        )

        if df.empty:
            return {
                "index": "^NSEI",
                "regime": "UNKNOWN",
                "confidence": 0,
            }

        close = df["Close"]

        current = float(close.iloc[-1])

        sma20 = float(close.rolling(20).mean().iloc[-1])
        sma50 = float(close.rolling(50).mean().iloc[-1])
        sma200 = float(close.rolling(200).mean().iloc[-1])

        if current > sma20 and sma20 > sma50 and sma50 > sma200:
            regime = "BULLISH"
            confidence = 90

        elif current < sma20 and sma20 < sma50 and sma50 < sma200:
            regime = "BEARISH"
            confidence = 90

        elif current > sma50:
            regime = "RECOVERY"
            confidence = 65

        elif current < sma50:
            regime = "CORRECTION"
            confidence = 65

        else:
            regime = "SIDEWAYS"
            confidence = 50

        return {
            "index": "^NSEI",
            "current": round(current, 2),
            "sma20": round(sma20, 2),
            "sma50": round(sma50, 2),
            "sma200": round(sma200, 2),
            "regime": regime,
            "confidence": confidence,
        }

    except Exception as e:
        return {
            "index": "^NSEI",
            "regime": "UNKNOWN",
            "confidence": 0,
            "error": str(e),
        }


def snapshot_market_regime():
    """
    Detect and store the current market regime.
    """

    from app.database import query

    result = detect_market_regime()

    if result.get("regime") == "UNKNOWN":
        return result

    query(
        """
        INSERT INTO market_regime_log
        (
            index_symbol,
            index_value,
            sma20,
            sma50,
            sma200,
            regime,
            confidence
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            result["index"],
            result["current"],
            result["sma20"],
            result["sma50"],
            result["sma200"],
            result["regime"],
            result["confidence"],
        ),
    )

    return result