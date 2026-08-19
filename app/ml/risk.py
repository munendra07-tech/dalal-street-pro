def calculate_risk(indicators):
    score = 50
    factors = []

    volatility = indicators.get("volatility_20")
    atr = indicators.get("atr")
    rsi = indicators.get("rsi")

    # Volatility
    if volatility is not None:

        if volatility > 0.035:
            score += 25
            factors.append("High recent volatility")

        elif volatility > 0.02:
            score += 12
            factors.append("Moderate recent volatility")

        else:
            score -= 8
            factors.append("Relatively stable volatility")

    # ATR
    if atr is not None:

        if atr > 0.04:
            score += 15
            factors.append("High ATR relative to price")

        elif atr < 0.015:
            score -= 5
            factors.append("Low ATR relative to price")

    # RSI extremes
    if rsi is not None:

        if rsi >= 75:
            score += 10
            factors.append("Strong overbought condition")

        elif rsi <= 25:
            score += 10
            factors.append("Strong oversold condition")

    score = max(0, min(100, score))

    if score <= 30:
        level = "LOW"

    elif score <= 60:
        level = "MEDIUM"

    elif score <= 80:
        level = "HIGH"

    else:
        level = "VERY HIGH"

    return {
        "score": score,
        "level": level,
        "factors": factors,
    }