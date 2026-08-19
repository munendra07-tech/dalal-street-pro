import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "return_1d",
    "return_5d",
    "return_20d",
    "sma20_ratio",
    "sma50_ratio",
    "sma200_ratio",
    "ema12_ratio",
    "ema26_ratio",
    "rsi",
    "macd",
    "macd_signal",
    "macd_histogram",
    "bollinger_position",
    "bollinger_width",
    "atr",
    "volatility_20",
    "volume_ratio",
    "volume_change",
    "momentum_10",
]


def calculate_rsi(close, period=14):
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    return 100 - (100 / (1 + rs))


def calculate_atr(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    previous_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - previous_close).abs()
    tr3 = (low - previous_close).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    return true_range.rolling(period).mean()


def create_features(df):
    df = df.copy()

    # -----------------------------
    # Returns
    # -----------------------------

    df["return_1d"] = df["Close"].pct_change()

    df["return_5d"] = (
        df["Close"].pct_change(5)
    )

    df["return_20d"] = (
        df["Close"].pct_change(20)
    )

    # -----------------------------
    # Moving averages
    # -----------------------------

    df["sma20"] = (
        df["Close"].rolling(20).mean()
    )

    df["sma50"] = (
        df["Close"].rolling(50).mean()
    )

    df["sma200"] = (
        df["Close"].rolling(200).mean()
    )

    # Price relative to moving averages

    df["sma20_ratio"] = (
        df["Close"] / df["sma20"] - 1
    )

    df["sma50_ratio"] = (
        df["Close"] / df["sma50"] - 1
    )

    df["sma200_ratio"] = (
        df["Close"] / df["sma200"] - 1
    )

    # -----------------------------
    # EMA
    # -----------------------------

    df["ema12"] = (
        df["Close"]
        .ewm(span=12, adjust=False)
        .mean()
    )

    df["ema26"] = (
        df["Close"]
        .ewm(span=26, adjust=False)
        .mean()
    )

    df["ema12_ratio"] = (
        df["Close"] / df["ema12"] - 1
    )

    df["ema26_ratio"] = (
        df["Close"] / df["ema26"] - 1
    )

    # -----------------------------
    # RSI
    # -----------------------------

    df["rsi"] = calculate_rsi(
        df["Close"]
    )

    # -----------------------------
    # MACD
    # -----------------------------

    df["macd"] = (
        df["ema12"] - df["ema26"]
    )

    df["macd_signal"] = (
        df["macd"]
        .ewm(span=9, adjust=False)
        .mean()
    )

    df["macd_histogram"] = (
        df["macd"] - df["macd_signal"]
    )

    # -----------------------------
    # Bollinger Bands
    # -----------------------------

    middle = (
        df["Close"].rolling(20).mean()
    )

    std = (
        df["Close"].rolling(20).std()
    )

    df["bollinger_upper"] = (
        middle + 2 * std
    )

    df["bollinger_lower"] = (
        middle - 2 * std
    )

    band_width = (
        df["bollinger_upper"]
        - df["bollinger_lower"]
    )

    df["bollinger_position"] = (
        (df["Close"] - df["bollinger_lower"])
        / band_width.replace(0, np.nan)
    )

    df["bollinger_width"] = (
        band_width / middle.replace(0, np.nan)
    )

    # -----------------------------
    # ATR
    # -----------------------------

    df["atr"] = calculate_atr(df)

    # Normalize ATR by price

    df["atr"] = (
        df["atr"] / df["Close"]
    )

    # -----------------------------
    # Volatility
    # -----------------------------

    df["volatility_20"] = (
        df["return_1d"]
        .rolling(20)
        .std()
    )

    # -----------------------------
    # Volume
    # -----------------------------

    volume_average = (
        df["Volume"].rolling(20).mean()
    )

    df["volume_ratio"] = (
        df["Volume"]
        / volume_average.replace(0, np.nan)
    )

    previous_volume = (
        df["Volume"].shift(1)
    )

    df["volume_change"] = (
        (df["Volume"] - previous_volume)
        / previous_volume.replace(0, np.nan)
    )

    # -----------------------------
    # Momentum
    # -----------------------------

    df["momentum_10"] = (
        df["Close"] / df["Close"].shift(10) - 1
    )

    # -----------------------------
    # Prediction target
    # -----------------------------

    df["target"] = (
        df["Close"].shift(-1) > df["Close"]
    ).astype(int)

    # -----------------------------
    # Clean data
    # -----------------------------

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return df


def prepare_training_data(df):
    df = create_features(df)

    df = df.dropna(
        subset=FEATURE_COLUMNS + ["target"]
    ).copy()

    X = df[FEATURE_COLUMNS].astype(float)

    y = df["target"].astype(int)

    return X, y, df