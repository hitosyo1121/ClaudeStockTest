"""Stock price and technicals router."""
from fastapi import APIRouter, HTTPException, Query
from ..schemas import StockPrice, StockTechnicals, StockSearchResult
from ..services import yfinance_service as yf_svc
from ..services.screening_service import load_universe

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/{code}/price", response_model=StockPrice)
def get_price(code: str):
    data = yf_svc.get_current_price(code)
    if data.get("price") is None:
        raise HTTPException(status_code=404, detail=f"株価が取得できませんでした: {code}")
    return StockPrice(**data)


@router.get("/{code}/technicals", response_model=StockTechnicals)
def get_technicals(code: str):
    data = yf_svc.get_technicals(code)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return StockTechnicals(**{k: v for k, v in data.items() if k in StockTechnicals.model_fields})


@router.get("/{code}/history")
def get_history(code: str, period: str = "3mo", interval: str = "1d"):
    df = yf_svc.get_history(code, period=period, interval=interval)
    if df is None:
        raise HTTPException(status_code=404, detail=f"履歴データが取得できませんでした: {code}")

    records = []
    for idx, row in df.iterrows():
        import pandas as pd
        records.append({
            "date": str(idx)[:10],
            "open": round(float(row["Open"]), 2) if pd.notna(row["Open"]) else None,
            "high": round(float(row["High"]), 2) if pd.notna(row["High"]) else None,
            "low": round(float(row["Low"]), 2) if pd.notna(row["Low"]) else None,
            "close": round(float(row["Close"]), 2) if pd.notna(row["Close"]) else None,
            "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else None,
        })
    return {"code": code, "period": period, "interval": interval, "data": records}


@router.get("/search", response_model=list[StockSearchResult])
def search_stocks(q: str = Query(..., min_length=1)):
    # Search from universe CSV first
    universe = load_universe()
    q_lower = q.lower()
    results = []
    for stock in universe:
        code = stock.get("code", "")
        name = stock.get("name", "")
        if q_lower in code.lower() or q_lower in name.lower():
            results.append(StockSearchResult(
                code=code,
                name=name,
                market=stock.get("market"),
                sector=stock.get("sector"),
            ))
    return results[:20]
