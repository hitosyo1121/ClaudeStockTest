from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, UniqueConstraint
from .database import Base


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_cost = Column(Float, nullable=False)
    market = Column(String, default="prime")
    sector = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PriceCache(Base):
    __tablename__ = "price_cache"

    code = Column(String, primary_key=True)
    price_type = Column(String, primary_key=True)
    data_json = Column(Text, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, index=True)
    run_date = Column(Date, nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    action = Column(String, nullable=False)  # 'buy' | 'sell' | 'watch'
    score = Column(Float, nullable=True)
    reasons_json = Column(Text, nullable=True)
    price_at_run = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class NewsCache(Base):
    __tablename__ = "news_cache"

    id = Column(Integer, primary_key=True, index=True)
    news_date = Column(Date, nullable=False)
    source = Column(String, nullable=True)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    relevance = Column(String, default="market")
    stock_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False)
    prediction_date = Column(Date, nullable=False)
    direction = Column(String, nullable=False)  # 'up' | 'down' | 'flat'
    confidence = Column(Float, nullable=True)
    predicted_range_low = Column(Float, nullable=True)
    predicted_range_high = Column(Float, nullable=True)
    hourly_json = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
