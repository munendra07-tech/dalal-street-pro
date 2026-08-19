def generate_explanation(
    prediction,
    indicators,
    model_probabilities,
):
    reasons = []
    warnings = []

    rsi = indicators.get("rsi")
    macd = indicators.get("macd")
    macd_signal = indicators.get("macd_signal")
    sma20 = indicators.get("sma20")
    sma50 = indicators.get("sma50")
    current_price = indicators.get("current_price")

    # RSI
    if rsi is not None:
        if rsi >= 70:
            reasons.append(
                "RSI is above 70, indicating overbought conditions."
            )
            warnings.append("Overbought momentum")

        elif rsi <= 30:
            reasons.append(
                "RSI is below 30, indicating oversold conditions."
            )
            reasons.append("Potential recovery momentum")

        elif rsi >= 55:
            reasons.append(
                "RSI shows moderately positive momentum."
            )

        elif rsi <= 45:
            reasons.append(
                "RSI shows moderately weak momentum."
            )

        else:
            reasons.append(
                "RSI is in a relatively neutral zone."
            )

    # MACD
    if macd is not None and macd_signal is not None:

        if macd > macd_signal:
            reasons.append(
                "MACD is above its signal line, supporting bullish momentum."
            )

        else:
            reasons.append(
                "MACD is below its signal line, indicating weaker momentum."
            )

    # SMA20
    if current_price is not None and sma20 is not None:

        if current_price > sma20:
            reasons.append(
                "Price is above the 20-day moving average."
            )

        else:
            reasons.append(
                "Price is below the 20-day moving average."
            )

    # SMA50
    if current_price is not None and sma50 is not None:

        if current_price > sma50:
            reasons.append(
                "Price is above the 50-day moving average."
            )

        else:
            reasons.append(
                "Price is below the 50-day moving average."
            )

    # Model agreement
    if model_probabilities:

        values = list(model_probabilities.values())

        if max(values) - min(values) < 0.10:
            reasons.append(
                "The models show relatively strong agreement."
            )

        else:
            warnings.append(
                "The models disagree on the market direction."
            )

    # Confidence warning
    confidence = prediction.get("confidence", 0)

    if confidence < 60:
        warnings.append(
            "Prediction confidence is relatively low."
        )

    elif confidence >= 70:
        reasons.append(
            "The ensemble has relatively strong directional confidence."
        )

    return {
        "reasons": reasons[:6],
        "warnings": warnings[:4],
        "summary": (
            f"The AI system currently indicates "
            f"{prediction.get('signal', 'HOLD')} "
            f"with {confidence:.2f}% confidence."
        ),
    }