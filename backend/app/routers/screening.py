"""TSE Screening router."""
import json
from datetime import date, datetime
from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ScreeningResult, Holding
from ..schemas import ScreeningResultResponse, ScreeningResponse
from ..services import screening_service, claude_service, yfinance_service as yf_svc

router = APIRouter(prefix="/api/screening", tags=["screening"])


@router.get("/results", response_model=ScreeningResponse)
def get_screening_results(db: Session = Depends(get_db)):
    today = date.today()

    results = (
        db.query(ScreeningResult)
        .filter(ScreeningResult.run_date == today)
        .order_by(ScreeningResult.score.desc())
        .all()
    )

    def to_resp(r: ScreeningResult) -> ScreeningResultResponse:
        reasons = None
        if r.reasons_json:
            try:
                reasons = json.loads(r.reasons_json)
            except Exception:
                reasons = [r.reasons_json]
        return ScreeningResultResponse(
            id=r.id,
            run_date=r.run_date,
            code=r.code,
            name=r.name,
            action=r.action,
            score=r.score,
            reasons=reasons,
            price_at_run=r.price_at_run,
            created_at=r.created_at,
        )

    buy = [to_resp(r) for r in results if r.action == "buy"]
    sell = [to_resp(r) for r in results if r.action == "sell"]
    watch = [to_resp(r) for r in results if r.action == "watch"]

    return ScreeningResponse(
        run_date=today,
        buy_recommendations=buy,
        sell_signals=sell,
        watch_list=watch,
    )


@router.post("/run")
def run_screening(db: Session = Depends(get_db)):
    """Run TSE screening and save results."""
    today = date.today()

    # Clear today's results
    db.query(ScreeningResult).filter(ScreeningResult.run_date == today).delete()
    db.commit()

    # Get holdings for sell signal check
    holdings = db.query(Holding).all()
    holdings_list = [
        {"code": h.code, "name": h.name, "quantity": h.quantity, "avg_cost": h.avg_cost}
        for h in holdings
    ]

    # Run technical screening
    candidates = screening_service.run_screening()

    # Get current prices for candidates
    candidate_codes = [c["code"] for c in candidates[:30]]
    if candidate_codes:
        prices = yf_svc.get_batch_prices(candidate_codes)
        for c in candidates:
            p = prices.get(c["code"], {})
            c["current_price"] = p.get("price")
            c["day_change_pct"] = p.get("day_change_pct")

    # Also check holdings for sell signals
    holding_codes = [h.code for h in holdings]
    if holding_codes:
        holding_prices = yf_svc.get_batch_prices(holding_codes)
        for h_dict in holdings_list:
            p = holding_prices.get(h_dict["code"], {})
            h_dict["current_price"] = p.get("price")
            if p.get("price"):
                h_dict["pnl_pct"] = round((p["price"] - h_dict["avg_cost"]) / h_dict["avg_cost"] * 100, 2)

    # Use Claude to select top 5 buys and sell signals
    ai_result = claude_service.generate_screening_recommendations(
        candidates[:30],
        holdings_list,
    )

    saved_count = 0

    # Save buy recommendations
    for rec in ai_result.get("buy_recommendations", [])[:5]:
        price_data = next((c for c in candidates if c["code"] == rec["code"]), {})
        result = ScreeningResult(
            run_date=today,
            code=rec["code"],
            name=rec.get("name", rec["code"]),
            action="buy",
            score=rec.get("score", 50),
            reasons_json=json.dumps(
                rec.get("reasons", []) + [f"目標株価: {rec.get('target_price', 'N/A')}"],
                ensure_ascii=False,
            ),
            price_at_run=price_data.get("current_price"),
        )
        db.add(result)
        saved_count += 1

    # Save sell signals
    for sig in ai_result.get("sell_signals", []):
        result = ScreeningResult(
            run_date=today,
            code=sig["code"],
            name=sig.get("name", sig["code"]),
            action="sell",
            score=None,
            reasons_json=json.dumps(sig.get("reasons", []), ensure_ascii=False),
            price_at_run=None,
        )
        db.add(result)

    # Save watch list (top candidates that didn't make buy list)
    buy_codes = {r.get("code") for r in ai_result.get("buy_recommendations", [])}
    for c in candidates[5:15]:
        if c["code"] not in buy_codes:
            result = ScreeningResult(
                run_date=today,
                code=c["code"],
                name=c.get("name", c["code"]),
                action="watch",
                score=c.get("score"),
                reasons_json=json.dumps(c.get("conditions_met", []), ensure_ascii=False),
                price_at_run=c.get("current_price"),
            )
            db.add(result)

    db.commit()

    return {
        "status": "ok",
        "run_date": str(today),
        "candidates_screened": len(candidates),
        "buy_recommendations": len(ai_result.get("buy_recommendations", [])),
        "sell_signals": len(ai_result.get("sell_signals", [])),
        "market_comment": ai_result.get("market_comment", ""),
    }
