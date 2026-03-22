"""FastAPI main application."""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import holdings, stocks, news, screening, predictions

# Create all tables on startup
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Stock Analysis API starting...")
    yield
    print("👋 Stock Analysis API shutting down...")


app = FastAPI(
    title="株式分析アプリ API",
    description="東証株式分析・保有株管理・AI予測",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(holdings.router)
app.include_router(stocks.router)
app.include_router(news.router)
app.include_router(screening.router)
app.include_router(predictions.router)


@app.get("/")
def root():
    return {"message": "株式分析アプリ API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
