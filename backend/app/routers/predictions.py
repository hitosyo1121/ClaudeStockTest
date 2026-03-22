"""AI Stock Prediction router."""
import json
from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Prediction, Holding
from ..schemas import PredictionResponse, HourlyForecast, PortfolioPrediction
from ..services import yfinance_service as yf_svc, claude_service

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


def _to_response(pred: Prediction) -> PredictionResponse:
    hourly = None
    if pred.hourly_json:
        try:
            raw = json.loads(pred.hourly_json)
            hourly = [
                HourlyForecast(
                    hour=item.get("hour", ""),
                    estimated_price=item.get("estimated_price", 0),
                    confidence_low=item.get("confidence_low"),
                    confidence_high=item.get("confidence_high"),
                )
                for item in raw
            ]
        except Exception:
            pass

    return PredictionResponse(
        id=pred.id,
        code=pred.code,
        prediction_date=pred.prediction_date,
        direction=pred.direction,
        confidence=pred.confidence,
        predicted_range_low=pred.predicted_range_low,
        predicted_range_high=pred.predicted_range_high,
        hourly_forecast=hourly,
        reasoning=pred.reasoning,
        generated_at=pred.generated_at,
    )


@router.get("/portfolio")
def get_portfolio_predictions(db: Session = Depends(get_db)):
    holdings = db.query(Holding).all()
    tomorrow = date.today() + timedelta(days=1)

    result = []
    codes = [h.code for h in holdings]
    prices = yf_svc.get_batch_prices(codes) if codes else {}

    for holding in holdings:
        pred = (
            db.query(Prediction)
            .filter(
                Prediction.code == holding.code,
                Prediction.prediction_date == tomorrow,
            )
            .order_by(Prediction.generated_at.desc())
            .first()
        )
        price_data = prices.get(holding.code, {})
        result.append({
            "code": holding.code,
            "name": holding.name,
            "current_price": price_data.get("price"),
            "prediction": _to_response(pred) if pred else None,
        })

    return result


@router.get("/{code}", response_model=Optional[PredictionResponse])
def get_prediction(code: str, db: Session = Depends(get_db)):
    tomorrow = date.today() + timedelta(days=1)
    pred = (
        db.query(Prediction)
        .filter(Prediction.code == code, Prediction.prediction_date == tomorrow)
        .order_by(Prediction.generated_at.desc())
        .first()
    )
    if not pred:
        return None
    return _to_response(pred)


@router.post("/generate/{code}", response_model=PredictionResponse)
def generate_prediction(code: str, db: Session = Depends(get_db)):
    """Generate AI prediction for a stock."""
    tomorrow = date.today() + timedelta(days=1)

    # Get price data
    price_data = yf_svc.get_current_price(code)
    current_price = price_data.get("price")
    if not current_price:
        raise HTTPException(status_code=404, detail=f"株価が取得できませんでした: {code}")

    # Get intraday and technical data
    intraday = yf_svc.get_intraday(code, period="5d", interval="1h") or []
    technicals = yf_svc.get_technicals(code)

    # Get related news from DB
    from ..models import NewsCache
    today = date.today()
    news = db.query(NewsCache).filter(NewsCache.news_date == today).limit(10).all()
    news_items = [{"title": n.title, "summary": n.summary} for n in news]

    # Get stock name from holdings or universe
    holding = db.query(Holding).filter(Holding.code == code).first()
    name = holding.name if holding else code

    # Generate prediction
    ai_result = claude_service.generate_stock_prediction(
        code=code,
        name=name,
        current_price=current_price,
        intraday_data=intraday,
        technicals=technicals,
        news_items=news_items,
    )

    # Save to DB
    pred = Prediction(
        code=code,
        prediction_date=tomorrow,
        direction=ai_result.get("direction", "flat"),
        confidence=ai_result.get("confidence", 0.5),
        predicted_range_low=ai_result.get("predicted_range_low"),
        predicted_range_high=ai_result.get("predicted_range_high"),
        hourly_json=json.dumps(
            ai_result.get("hourly_forecast", []),
            ensure_ascii=False,
        ),
        reasoning=ai_result.get("reasoning", ""),
        generated_at=datetime.utcnow(),
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    return _to_response(pred)
