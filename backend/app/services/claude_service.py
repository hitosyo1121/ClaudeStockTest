"""Claude API service for AI-powered analysis."""
import json
import logging
import os
from typing import Optional
import anthropic

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"


def _get_client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set")
    return anthropic.Anthropic(api_key=api_key)


def summarize_news(news_items: list[dict], target_date: str) -> dict:
    """Summarize news items and generate market outlook."""
    if not news_items:
        return {"summary": "ニュースデータが取得できませんでした。", "outlook": ""}

    news_text = "\n".join(
        f"- [{item.get('source', '')}] {item.get('title', '')} | {item.get('summary', '')[:150]}"
        for item in news_items[:20]
    )

    prompt = f"""以下は{target_date}の日本株式市場に関連するニュースです。

{news_text}

以下の形式でJSON出力してください：
{{
  "market_summary": "市場全体への影響を3-5文で日本語で要約",
  "key_themes": ["テーマ1", "テーマ2", "テーマ3"],
  "sentiment": "bullish|bearish|neutral",
  "top_items": [
    {{"title": "重要ニュースタイトル", "impact": "市場への影響を1文で"}}
  ]
}}"""

    try:
        client = _get_client()
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        # Extract JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Claude news summary error: {e}")
        return {
            "market_summary": "AI要約の生成中にエラーが発生しました。",
            "key_themes": [],
            "sentiment": "neutral",
            "top_items": [],
        }


def generate_tomorrow_outlook(today_news: list[dict], holdings: list[dict]) -> dict:
    """Generate tomorrow's market outlook based on today's news and scheduled events."""
    news_text = "\n".join(
        f"- {item.get('title', '')}"
        for item in today_news[:15]
    )
    holdings_text = ", ".join(f"{h.get('name', h.get('code', ''))}({h.get('code', '')})" for h in holdings[:10])

    prompt = f"""あなたは東京証券取引所の株式市場アナリストです。

【今日のニュース】
{news_text}

【保有銘柄】
{holdings_text}

明日の日本株式市場の動向を以下の形式でJSON出力してください：
{{
  "overall_direction": "上昇|下落|横ばい",
  "confidence": 0.0～1.0の数値,
  "key_factors": [
    {{"factor": "要因の説明", "impact": "positive|negative|neutral", "magnitude": "high|medium|low"}}
  ],
  "sector_outlook": [
    {{"sector": "セクター名", "direction": "上昇|下落|横ばい", "reason": "理由"}}
  ],
  "scheduled_events": ["予定されているイベント（決算発表、指標発表等）"],
  "risk_factors": ["注意すべきリスク要因"],
  "summary": "明日の市場見通しの総括（3-5文）",
  "hourly_trend": [
    {{"time_range": "09:00-10:00", "trend": "上昇|下落|横ばい", "note": "補足"}}
  ]
}}

注意：これはAIによる参考情報であり、投資判断の根拠にはなりません。"""

    try:
        client = _get_client()
        message = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Claude tomorrow outlook error: {e}")
        return {
            "overall_direction": "横ばい",
            "confidence": 0.5,
            "key_factors": [],
            "sector_outlook": [],
            "scheduled_events": [],
            "risk_factors": [],
            "summary": "AI見通しの生成中にエラーが発生しました。",
            "hourly_trend": [],
        }


def generate_stock_prediction(
    code: str,
    name: str,
    current_price: float,
    intraday_data: list[dict],
    technicals: dict,
    news_items: list[dict],
) -> dict:
    """Generate price prediction for a stock using Claude."""
    tech_text = json.dumps(technicals, ensure_ascii=False, indent=2)
    intraday_text = json.dumps(intraday_data[-20:] if intraday_data else [], ensure_ascii=False)
    news_text = "\n".join(f"- {item.get('title', '')}" for item in news_items[:10])

    prompt = f"""あなたは株式アナリストです。以下のデータに基づいて{name}（{code}）の明日の株価動向を予測してください。

【現在株価】{current_price}円

【テクニカル指標】
{tech_text}

【直近の1時間足データ（最新20本）】
{intraday_text}

【関連ニュース】
{news_text}

以下の形式でJSONを出力してください：
{{
  "direction": "up|down|flat",
  "confidence": 0.0～1.0の数値,
  "predicted_range_low": 予測下限株価（円）,
  "predicted_range_high": 予測上限株価（円）,
  "hourly_forecast": [
    {{"hour": "09:00", "estimated_price": 株価, "note": ""}},
    {{"hour": "10:00", "estimated_price": 株価, "note": ""}},
    {{"hour": "11:00", "estimated_price": 株価, "note": ""}},
    {{"hour": "12:00", "estimated_price": 株価, "note": ""}},
    {{"hour": "13:00", "estimated_price": 株価, "note": ""}},
    {{"hour": "14:00", "estimated_price": 株価, "note": ""}},
    {{"hour": "15:00", "estimated_price": 株価, "note": ""}}
  ],
  "key_signals": ["重要なシグナルや根拠"],
  "risk_factors": ["下落リスク要因"],
  "reasoning": "予測の根拠を日本語で3-5文で説明"
}}

⚠️ これはAIによる参考情報であり、投資判断の根拠にはなりません。"""

    try:
        client = _get_client()
        message = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Claude prediction error for {code}: {e}")
        return {
            "direction": "flat",
            "confidence": 0.5,
            "predicted_range_low": current_price * 0.97,
            "predicted_range_high": current_price * 1.03,
            "hourly_forecast": [],
            "key_signals": [],
            "risk_factors": [],
            "reasoning": "予測の生成中にエラーが発生しました。",
        }


def generate_screening_recommendations(
    candidates: list[dict],
    holdings: list[dict],
    market_context: str = "",
) -> dict:
    """Use Claude to select top 5 buy recommendations and sell signals from screened candidates."""
    if not candidates:
        return {"buy": [], "sell": []}

    candidates_text = json.dumps(candidates[:30], ensure_ascii=False, indent=2)
    holdings_text = json.dumps(holdings, ensure_ascii=False, indent=2)

    prompt = f"""あなたは東証の株式アナリストです。以下のスクリーニング候補銘柄と保有銘柄を分析してください。

【スクリーニング候補銘柄（テクニカル・ファンダスコア付き）】
{candidates_text}

【現在の保有銘柄】
{holdings_text}

【市場環境】
{market_context}

東証短期高騰銘柄スクリーニング基準（RSI40-65、MA25上向き、MACD好転等）に基づいて分析し、以下のJSON形式で出力してください：

{{
  "buy_recommendations": [
    {{
      "code": "銘柄コード",
      "name": "銘柄名",
      "score": 0-100のスコア,
      "reasons": ["購入推奨理由1", "理由2", "理由3"],
      "catalysts": ["上昇カタリスト"],
      "risk_factors": ["リスク要因"],
      "target_price": 目標株価,
      "stop_loss": 損切り価格,
      "holding_period": "想定保有期間（例：1-2週間）"
    }}
  ],
  "sell_signals": [
    {{
      "code": "銘柄コード",
      "name": "銘柄名",
      "reasons": ["売却推奨理由"],
      "urgency": "high|medium|low"
    }}
  ],
  "market_comment": "現在の市場環境についてのコメント"
}}

購入推奨は最大5銘柄、売却シグナルは保有銘柄の中から該当するものを選出してください。
⚠️ これはAIによる参考情報であり、投資判断の根拠にはなりません。"""

    try:
        client = _get_client()
        message = client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        logger.error(f"Claude screening error: {e}")
        return {"buy_recommendations": [], "sell_signals": [], "market_comment": ""}
