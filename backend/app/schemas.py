from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# --- Holdings ---
class HoldingCreate(BaseModel):
    code: str = Field(..., description="銘柄コード（例: 6501）")
    name: str = Field(..., description="銘柄名")
    quantity: int = Field(..., gt=0)
    avg_cost: float = Field(..., gt=0, description="平均取得単価（円）")
    market: str = Field(default="prime", description="prime|standard|growth")
    sector: Optional[str] = None


class HoldingUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = Field(None, gt=0)
    avg_cost: Optional[float] = Field(None, gt=0)
    market: Optional[str] = None
    sector: Optional[str] = None


class HoldingResponse(BaseModel):
    id: int
    code: str
    name: str
    quantity: int
    avg_cost: float
    market: str
    sector: Optional[str]
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    day_change: Optional[float] = None
    day_change_pct: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Stocks ---
class StockPrice(BaseModel):
    code: str
    price: Optional[float]
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None
    day_change: Optional[float] = None
    day_change_pct: Optional[float] = None
    timestamp: Optional[datetime] = None


class StockTechnicals(BaseModel):
    code: str
    ma25: Optional[float] = None
    ma75: Optional[float] = None
    ma25_slope: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    ichimoku_above_cloud: Optional[bool] = None
    trend: Optional[str] = None  # 'bullish' | 'bearish' | 'neutral'


class StockSearchResult(BaseModel):
    code: str
    name: str
    market: Optional[str] = None
    sector: Optional[str] = None


# --- News ---
class NewsItem(BaseModel):
    id: int
    news_date: date
    source: Optional[str]
    title: str
    summary: Optional[str]
    url: Optional[str]
    relevance: str
    stock_code: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class NewsResponse(BaseModel):
    date: date
    items: List[NewsItem]
    market_summary: Optional[str] = None
    outlook: Optional[str] = None


# --- Screening ---
class ScreeningResultResponse(BaseModel):
    id: int
    run_date: date
    code: str
    name: str
    action: str
    score: Optional[float]
    reasons: Optional[List[str]] = None
    price_at_run: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class ScreeningResponse(BaseModel):
    run_date: date
    buy_recommendations: List[ScreeningResultResponse]
    sell_signals: List[ScreeningResultResponse]
    watch_list: List[ScreeningResultResponse]


# --- Predictions ---
class HourlyForecast(BaseModel):
    hour: str
    estimated_price: float
    confidence_low: Optional[float] = None
    confidence_high: Optional[float] = None


class PredictionResponse(BaseModel):
    id: int
    code: str
    prediction_date: date
    direction: str
    confidence: Optional[float]
    predicted_range_low: Optional[float]
    predicted_range_high: Optional[float]
    hourly_forecast: Optional[List[HourlyForecast]] = None
    reasoning: Optional[str]
    generated_at: datetime

    model_config = {"from_attributes": True}


class PortfolioPrediction(BaseModel):
    code: str
    name: str
    current_price: Optional[float]
    prediction: Optional[PredictionResponse]
