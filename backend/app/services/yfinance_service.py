"""Yahoo Finance data fetching service using direct API calls."""
import logging
from datetime import datetime, timedelta
from typing import Optional
import asyncio
import httpx
import pandas as pd
import pytz
from . import indicators as ta

logger = logging.getLogger(__name__)
JST = pytz.timezone("Asia/Tokyo")

YF_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
}
YF_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"
YF_BASE2 = "https://query2.finance.yahoo.com/v8/finance/chart"


def _ticker(code: str) -> str:
    code = code.strip()
    if not code.endswith(".T"):
        return f"{code}.T"
    return code


def is_market_open() -> bool:
    now_jst = datetime.now(JST)
    if now_jst.weekday() >= 5:
        return False
    market_open = now_jst.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close = now_jst.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now_jst <= market_close


def _fetch_chart(ticker: str, interval: str = "1d", range_: str = "3mo") -> Optional[dict]:
    """Fetch chart data from Yahoo Finance v8 API."""
    url = f"{YF_BASE}/{ticker}"
    params = {"interval": interval, "range": range_}
    for base in [YF_BASE, YF_BASE2]:
        try:
            url = f"{base}/{ticker}"
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                r = client.get(url, params=params, headers=YF_HEADERS)
                if r.status_code == 200:
                    data = r.json()
                    results = data.get("chart", {}).get("result")
                    if results:
                        return results[0]
        except Exception as e:
            logger.debug(f"Chart fetch attempt failed for {ticker}: {e}")
    return None


def _chart_to_df(chart: dict) -> Optional[pd.DataFrame]:
    """Convert Yahoo Finance chart response to DataFrame."""
    try:
        timestamps = chart.get("timestamp", [])
        quote = chart["indicators"]["quote"][0]
        if not timestamps:
            return None

        df = pd.DataFrame({
            "Open": quote.get("open", []),
            "High": quote.get("high", []),
            "Low": quote.get("low", []),
            "Close": quote.get("close", []),
            "Volume": quote.get("volume", []),
        }, index=pd.to_datetime(timestamps, unit="s", utc=True))

        df.index = df.index.tz_convert(JST)
        df = df.dropna(subset=["Close"])
        return df
    except Exception as e:
        logger.warning(f"Chart to df conversion error: {e}")
        return None


def get_current_price(code: str) -> dict:
    """Fetch current price info for a single stock."""
    chart = _fetch_chart(_ticker(code), interval="1d", range_="5d")
    if not chart:
        return {"code": code, "price": None}

    try:
        meta = chart.get("meta", {})
        price = meta.get("regularMarketPrice") or meta.get("previousClose")
        open_p = meta.get("regularMarketOpen")
        high = meta.get("regularMarketDayHigh")
        low = meta.get("regularMarketDayLow")
        volume = meta.get("regularMarketVolume")

        df = _chart_to_df(chart)
        day_change = None
        day_change_pct = None
        if df is not None and len(df) >= 2:
            prev_close = float(df["Close"].iloc[-2])
            curr_close = price or float(df["Close"].iloc[-1])
            if prev_close and curr_close:
                day_change = round(curr_close - prev_close, 2)
                day_change_pct = round((day_change / prev_close) * 100, 2)

        return {
            "code": code,
            "price": float(price) if price else None,
            "open": float(open_p) if open_p else None,
            "high": float(high) if high else None,
            "low": float(low) if low else None,
            "volume": int(volume) if volume else None,
            "day_change": day_change,
            "day_change_pct": day_change_pct,
            "timestamp": datetime.now(JST).isoformat(),
        }
    except Exception as e:
        logger.warning(f"Price parse error for {code}: {e}")
        return {"code": code, "price": None}


def get_batch_prices(codes: list[str]) -> dict[str, dict]:
    """Fetch prices for multiple stocks (sequential with rate limiting)."""
    results = {}
    for i, code in enumerate(codes):
        if i > 0 and i % 5 == 0:
            import time; time.sleep(0.5)
        results[code] = get_current_price(code)
    return results


def get_history(code: str, period: str = "3mo", interval: str = "1d") -> Optional[pd.DataFrame]:
    """Fetch historical OHLCV data as DataFrame."""
    chart = _fetch_chart(_ticker(code), interval=interval, range_=period)
    if not chart:
        return None
    return _chart_to_df(chart)


def get_technicals(code: str) -> dict:
    """Calculate technical indicators for a stock."""
    df = get_history(code, period="6mo", interval="1d")
    if df is None or len(df) < 30:
        return {"code": code, "error": "insufficient data"}

    result = {"code": code}

    try:
        df["MA25"] = df["Close"].rolling(25).mean()
        df["MA75"] = df["Close"].rolling(75).mean()

        ma25 = df["MA25"].iloc[-1]
        ma75 = df["MA75"].iloc[-1] if len(df) >= 75 else None

        result["ma25"] = round(float(ma25), 2) if pd.notna(ma25) else None
        result["ma75"] = round(float(ma75), 2) if ma75 is not None and pd.notna(ma75) else None

        if len(df) >= 30:
            ma25_5d_ago = df["MA25"].iloc[-6]
            if pd.notna(ma25_5d_ago) and pd.notna(ma25):
                result["ma25_slope"] = round(float(ma25 - ma25_5d_ago), 2)

        rsi_series = ta.rsi(df["Close"], length=14)
        if rsi_series is not None and not rsi_series.empty:
            rsi_val = rsi_series.iloc[-1]
            result["rsi"] = round(float(rsi_val), 2) if pd.notna(rsi_val) else None

        macd_df = ta.macd(df["Close"])
        if macd_df is not None and not macd_df.empty:
            result["macd"] = round(float(macd_df["MACD"].iloc[-1]), 4) if pd.notna(macd_df["MACD"].iloc[-1]) else None
            result["macd_signal"] = round(float(macd_df["Signal"].iloc[-1]), 4) if pd.notna(macd_df["Signal"].iloc[-1]) else None
            result["macd_hist"] = round(float(macd_df["Hist"].iloc[-1]), 4) if pd.notna(macd_df["Hist"].iloc[-1]) else None

        bb_df = ta.bbands(df["Close"], length=20)
        if bb_df is not None and not bb_df.empty:
            result["bb_upper"] = round(float(bb_df["Upper"].iloc[-1]), 2) if pd.notna(bb_df["Upper"].iloc[-1]) else None
            result["bb_middle"] = round(float(bb_df["Middle"].iloc[-1]), 2) if pd.notna(bb_df["Middle"].iloc[-1]) else None
            result["bb_lower"] = round(float(bb_df["Lower"].iloc[-1]), 2) if pd.notna(bb_df["Lower"].iloc[-1]) else None

        try:
            ich = ta.ichimoku(df["High"], df["Low"], df["Close"])
            current_price = df["Close"].iloc[-1]
            sa = ich["senkou_a"].iloc[-1]
            sb = ich["senkou_b"].iloc[-1]
            if pd.notna(sa) and pd.notna(sb):
                cloud_top = max(float(sa), float(sb))
                result["ichimoku_above_cloud"] = bool(float(current_price) > cloud_top)
        except Exception:
            pass

        current_price = float(df["Close"].iloc[-1])
        if result.get("ma25") and result.get("ma75"):
            if current_price > result["ma25"] > result["ma75"] and result.get("ma25_slope", 0) > 0:
                result["trend"] = "bullish"
            elif current_price < result.get("ma25", current_price):
                result["trend"] = "bearish"
            else:
                result["trend"] = "neutral"
        else:
            result["trend"] = "neutral"

    except Exception as e:
        logger.warning(f"Error computing technicals for {code}: {e}")

    return result


def get_intraday(code: str, period: str = "5d", interval: str = "1h") -> Optional[list]:
    """Get intraday OHLCV data as list of dicts."""
    chart = _fetch_chart(_ticker(code), interval=interval, range_=period)
    if not chart:
        return None

    df = _chart_to_df(chart)
    if df is None:
        return None

    records = []
    for idx, row in df.iterrows():
        records.append({
            "datetime": str(idx),
            "open": round(float(row["Open"]), 2) if pd.notna(row["Open"]) else None,
            "high": round(float(row["High"]), 2) if pd.notna(row["High"]) else None,
            "low": round(float(row["Low"]), 2) if pd.notna(row["Low"]) else None,
            "close": round(float(row["Close"]), 2) if pd.notna(row["Close"]) else None,
            "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else None,
        })
    return records[-50:]


def search_stock(query: str) -> list[dict]:
    """Search stocks using Yahoo Finance search endpoint."""
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        params = {"q": query, "lang": "ja", "region": "JP", "quotesCount": 10}
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url, params=params, headers=YF_HEADERS)
            if r.status_code == 200:
                data = r.json()
                results = []
                for q in data.get("quotes", []):
                    if q.get("exchange") in ["JPX", "TYO", "OSA"]:
                        code = q.get("symbol", "").replace(".T", "")
                        results.append({
                            "code": code,
                            "name": q.get("longname") or q.get("shortname", code),
                            "market": "prime",
                            "sector": q.get("industry"),
                        })
                return results[:10]
    except Exception as e:
        logger.warning(f"Search failed: {e}")
    return []
