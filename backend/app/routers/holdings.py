"""Holdings CRUD router."""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Holding
from ..schemas import HoldingCreate, HoldingUpdate, HoldingResponse
from ..services import yfinance_service as yf_svc

router = APIRouter(prefix="/api/holdings", tags=["holdings"])


def _enrich_with_price(holding: Holding, price_data: dict) -> dict:
    d = {
        "id": holding.id,
        "code": holding.code,
        "name": holding.name,
        "quantity": holding.quantity,
        "avg_cost": holding.avg_cost,
        "market": holding.market,
        "sector": holding.sector,
        "created_at": holding.created_at,
        "updated_at": holding.updated_at,
        "current_price": None,
        "market_value": None,
        "unrealized_pnl": None,
        "pnl_pct": None,
        "day_change": None,
        "day_change_pct": None,
    }
    price = price_data.get("price")
    if price:
        d["current_price"] = price
        d["market_value"] = round(price * holding.quantity, 0)
        d["unrealized_pnl"] = round((price - holding.avg_cost) * holding.quantity, 0)
        d["pnl_pct"] = round((price - holding.avg_cost) / holding.avg_cost * 100, 2)
        d["day_change"] = price_data.get("day_change")
        d["day_change_pct"] = price_data.get("day_change_pct")
    return d


@router.get("", response_model=List[HoldingResponse])
def list_holdings(db: Session = Depends(get_db)):
    holdings = db.query(Holding).order_by(Holding.code).all()
    if not holdings:
        return []

    codes = [h.code for h in holdings]
    prices = yf_svc.get_batch_prices(codes)

    result = []
    for h in holdings:
        price_data = prices.get(h.code, {"code": h.code, "price": None})
        result.append(_enrich_with_price(h, price_data))
    return result


@router.post("", response_model=HoldingResponse, status_code=201)
def create_holding(payload: HoldingCreate, db: Session = Depends(get_db)):
    existing = db.query(Holding).filter(Holding.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"銘柄コード {payload.code} は既に登録されています")

    holding = Holding(**payload.model_dump())
    db.add(holding)
    db.commit()
    db.refresh(holding)

    price_data = yf_svc.get_current_price(holding.code)
    return _enrich_with_price(holding, price_data)


@router.put("/{holding_id}", response_model=HoldingResponse)
def update_holding(holding_id: int, payload: HoldingUpdate, db: Session = Depends(get_db)):
    holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="保有株が見つかりません")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(holding, key, value)
    holding.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(holding)

    price_data = yf_svc.get_current_price(holding.code)
    return _enrich_with_price(holding, price_data)


@router.delete("/{holding_id}", status_code=204)
def delete_holding(holding_id: int, db: Session = Depends(get_db)):
    holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="保有株が見つかりません")
    db.delete(holding)
    db.commit()
