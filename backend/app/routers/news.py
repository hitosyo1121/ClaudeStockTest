"""News router."""
import asyncio
from datetime import date, datetime
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import NewsCache, Holding
from ..schemas import NewsItem, NewsResponse
from ..services import news_service, claude_service

router = APIRouter(prefix="/api/news", tags=["news"])


def _save_news_to_db(db: Session, items: list[dict], news_date: date):
    """Save news items to DB cache."""
    for item in items:
        db_item = NewsCache(
            news_date=news_date,
            source=item.get("source"),
            title=item.get("title", "")[:500],
            summary=item.get("summary"),
            url=item.get("url"),
            relevance=item.get("relevance", "market"),
            stock_code=item.get("stock_code"),
        )
        db.add(db_item)
    try:
        db.commit()
    except Exception:
        db.rollback()


async def _fetch_and_cache(db: Session, target_date: date) -> tuple[list, dict]:
    """Fetch fresh news and store in DB."""
    raw_items = await news_service.fetch_all_news()
    holdings = db.query(Holding).all()
    holding_codes = [h.code for h in holdings]

    categorized = news_service.categorize_news(raw_items, holding_codes)

    # Save to DB
    _save_news_to_db(db, categorized, target_date)

    # Get AI summary
    summary_data = claude_service.summarize_news(categorized, str(target_date))
    return categorized, summary_data


@router.get("/today", response_model=NewsResponse)
async def get_today_news(db: Session = Depends(get_db)):
    today = date.today()

    # Check cache
    cached = db.query(NewsCache).filter(NewsCache.news_date == today).all()

    if not cached:
        # Fetch fresh
        raw_items, summary_data = await _fetch_and_cache(db, today)
        cached = db.query(NewsCache).filter(NewsCache.news_date == today).all()
    else:
        # Regenerate summary from cached
        raw_items = [
            {"title": c.title, "summary": c.summary, "source": c.source}
            for c in cached
        ]
        summary_data = claude_service.summarize_news(raw_items, str(today))

    items = [NewsItem.model_validate(c) for c in cached[:30]]

    return NewsResponse(
        date=today,
        items=items,
        market_summary=summary_data.get("market_summary", ""),
        outlook=None,
    )


@router.get("/tomorrow")
async def get_tomorrow_outlook(db: Session = Depends(get_db)):
    today = date.today()
    cached = db.query(NewsCache).filter(NewsCache.news_date == today).all()

    raw_items = [
        {"title": c.title, "summary": c.summary, "source": c.source}
        for c in cached[:20]
    ]

    if not raw_items:
        # Try fetching first
        raw_items_full, _ = await _fetch_and_cache(db, today)
        raw_items = raw_items_full[:20]

    holdings = db.query(Holding).all()
    holdings_list = [{"code": h.code, "name": h.name} for h in holdings]

    outlook = claude_service.generate_tomorrow_outlook(raw_items, holdings_list)

    return {
        "prediction_for": str(today),
        "generated_at": datetime.now().isoformat(),
        **outlook,
    }


@router.post("/refresh")
async def refresh_news(db: Session = Depends(get_db)):
    today = date.today()
    # Clear today's cache
    db.query(NewsCache).filter(NewsCache.news_date == today).delete()
    db.commit()

    raw_items, summary_data = await _fetch_and_cache(db, today)
    return {"status": "ok", "items_fetched": len(raw_items)}
