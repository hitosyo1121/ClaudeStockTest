"""Technical indicator calculations using pure pandas/numpy."""
import numpy as np
import pandas as pd


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=length - 1, min_periods=length).mean()
    avg_loss = loss.ewm(com=length - 1, min_periods=length).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({"MACD": macd_line, "Signal": signal_line, "Hist": histogram})


def bbands(close: pd.Series, length: int = 20, std: float = 2.0) -> pd.DataFrame:
    middle = close.rolling(length).mean()
    std_dev = close.rolling(length).std()
    upper = middle + std * std_dev
    lower = middle - std * std_dev
    return pd.DataFrame({"Upper": upper, "Middle": middle, "Lower": lower})


def ichimoku(high: pd.Series, low: pd.Series, close: pd.Series) -> dict:
    """Simplified Ichimoku Cloud."""
    # Tenkan-sen (9)
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
    # Kijun-sen (26)
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
    # Senkou Span A
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    # Senkou Span B
    senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)

    return {
        "tenkan": tenkan,
        "kijun": kijun,
        "senkou_a": senkou_a,
        "senkou_b": senkou_b,
    }
