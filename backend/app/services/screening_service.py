"""TSE Stock Screening Service based on the specified criteria."""
import csv
import json
import logging
from pathlib import Path
from typing import Optional
import pandas as pd
from . import indicators as ta
from . import yfinance_service as yf_svc

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UNIVERSE_CSV = BASE_DIR / "data" / "tse_universe.csv"


def load_universe() -> list[dict]:
    """Load the TSE stock universe from CSV."""
    if not UNIVERSE_CSV.exists():
        logger.warning("TSE universe CSV not found, using empty list")
        return []
    stocks = []
    with open(UNIVERSE_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stocks.append(row)
    return stocks


def screen_stock(code: str, df: Optional[pd.DataFrame]) -> dict:
    """Apply TSE screening criteria to a single stock."""
    result = {
        "code": code,
        "pass": False,
        "score": 0,
        "conditions_met": [],
        "conditions_failed": [],
        "exclude": False,
        "exclude_reason": None,
    }

    if df is None or len(df) < 30:
        result["exclude"] = True
        result["exclude_reason"] = "insufficient data"
        return result

    try:
        # Flatten MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close = df["Close"]
        volume = df["Volume"]
        current_price = float(close.iloc[-1])

        # --- Exclusion filters ---
        # 5-day return > 15%
        if len(close) >= 6:
            ret_5d = (current_price - float(close.iloc[-6])) / float(close.iloc[-6]) * 100
            if ret_5d > 15:
                result["exclude"] = True
                result["exclude_reason"] = f"5日騰落率{ret_5d:.1f}%（+15%超）"
                return result

        # Volume spike > 200% of 5-day average
        if len(volume) >= 6:
            avg_vol = float(volume.iloc[-6:-1].mean())
            curr_vol = float(volume.iloc[-1])
            if avg_vol > 0 and curr_vol > avg_vol * 2:
                result["exclude"] = True
                result["exclude_reason"] = "出来高急増（平均比200%超）"
                return result

        # Price range filter 200-10000
        if not (200 <= current_price <= 10000):
            result["exclude"] = True
            result["exclude_reason"] = f"株価{current_price}円（対象外レンジ）"
            return result

        score = 0

        # --- Technical conditions ---
        # MA25 upward
        ma25 = close.rolling(25).mean()
        if len(ma25) >= 30 and pd.notna(ma25.iloc[-1]) and pd.notna(ma25.iloc[-6]):
            if ma25.iloc[-1] > ma25.iloc[-6]:
                score += 15
                result["conditions_met"].append("MA25上向き")
            else:
                result["conditions_failed"].append("MA25下向き")

        # Price above MA25 and MA75
        if pd.notna(ma25.iloc[-1]):
            if current_price > ma25.iloc[-1]:
                score += 10
                result["conditions_met"].append("株価>MA25")
            else:
                result["conditions_failed"].append("株価<MA25")

        ma75 = close.rolling(75).mean()
        if len(close) >= 75 and pd.notna(ma75.iloc[-1]):
            if current_price > ma75.iloc[-1]:
                score += 10
                result["conditions_met"].append("株価>MA75")
            else:
                result["conditions_failed"].append("株価<MA75")

        # RSI 40-65
        rsi_series = ta.rsi(close, length=14)
        if rsi_series is not None and pd.notna(rsi_series.iloc[-1]):
            rsi = float(rsi_series.iloc[-1])
            result["rsi"] = round(rsi, 2)
            if 40 <= rsi <= 65:
                score += 15
                result["conditions_met"].append(f"RSI={rsi:.1f}（40-65）")
            else:
                result["conditions_failed"].append(f"RSI={rsi:.1f}（範囲外）")

        # MACD crossover
        macd_df = ta.macd(close)
        if macd_df is not None and not macd_df.empty and len(macd_df) >= 2:
            hist_now = macd_df["Hist"].iloc[-1]
            hist_prev = macd_df["Hist"].iloc[-2]
            if pd.notna(hist_now) and pd.notna(hist_prev):
                if hist_now > 0 or (hist_now > hist_prev and hist_prev < 0):
                    score += 15
                    result["conditions_met"].append("MACDゴールデンクロス/好転")
                else:
                    result["conditions_failed"].append("MACD未好転")

        # 5-day price change -3% to +8%
        if len(close) >= 6:
            ret_5d = (current_price - float(close.iloc[-6])) / float(close.iloc[-6]) * 100
            result["ret_5d"] = round(ret_5d, 2)
            if -3 <= ret_5d <= 8:
                score += 10
                result["conditions_met"].append(f"5日騰落率{ret_5d:.1f}%（適正）")
            else:
                result["conditions_failed"].append(f"5日騰落率{ret_5d:.1f}%（範囲外）")

        # 20-day price change +5% to +25%
        if len(close) >= 21:
            ret_20d = (current_price - float(close.iloc[-21])) / float(close.iloc[-21]) * 100
            result["ret_20d"] = round(ret_20d, 2)
            if 5 <= ret_20d <= 25:
                score += 10
                result["conditions_met"].append(f"20日騰落率{ret_20d:.1f}%（適正）")

        # Volume in 50-150% of 5-day average
        if len(volume) >= 6:
            avg_vol_5d = float(volume.iloc[-6:-1].mean())
            curr_vol = float(volume.iloc[-1])
            if avg_vol_5d > 0:
                vol_ratio = curr_vol / avg_vol_5d * 100
                result["volume_ratio"] = round(vol_ratio, 1)
                if 50 <= vol_ratio <= 150:
                    score += 10
                    result["conditions_met"].append(f"出来高比{vol_ratio:.0f}%（適正）")

        # Ichimoku above cloud
        try:
            ich = ta.ichimoku(df["High"], df["Low"], close)
            sa = ich["senkou_a"].iloc[-1]
            sb = ich["senkou_b"].iloc[-1]
            if pd.notna(sa) and pd.notna(sb):
                cloud_top = max(sa, sb)
                if current_price > cloud_top:
                    score += 5
                    result["conditions_met"].append("一目均衡表雲の上")
        except Exception:
            pass

        result["score"] = min(score, 100)
        result["current_price"] = round(current_price, 2)

        # Minimum threshold to pass
        if score >= 40 and len(result["conditions_met"]) >= 3:
            result["pass"] = True

    except Exception as e:
        logger.warning(f"Screening error for {code}: {e}")
        result["exclude"] = True
        result["exclude_reason"] = f"計算エラー: {e}"

    return result


def run_screening(universe: Optional[list[dict]] = None, batch_size: int = 40) -> list[dict]:
    """Run TSE screening on the universe of stocks."""
    if universe is None:
        universe = load_universe()

    if not universe:
        logger.warning("Universe is empty")
        return []

    logger.info(f"Screening {len(universe)} stocks...")
    passed = []

    # Process individually using direct API calls (rate-limited)
    import time
    for i, stock in enumerate(universe):
        if i > 0 and i % 10 == 0:
            time.sleep(1)  # Rate limiting

        try:
            df = yf_svc.get_history(code, period="6mo", interval="1d")
            result = screen_stock(code, df)
            result["name"] = stock.get("name", code)
            result["market"] = stock.get("market", "prime")
            result["sector"] = stock.get("sector", "")

            if result["pass"] and not result["exclude"]:
                passed.append(result)

        except Exception as e:
            logger.debug(f"Skip {code}: {e}")
            continue

    # Sort by score descending
    passed.sort(key=lambda x: x.get("score", 0), reverse=True)
    logger.info(f"Screening complete: {len(passed)} stocks passed")
    return passed
