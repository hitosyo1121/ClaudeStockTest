"""News fetching service via RSS feeds using built-in XML parser."""
import logging
import re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional
import asyncio
import httpx
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

RSS_FEEDS = [
    {
        "name": "NHK経済",
        "url": "https://www3.nhk.or.jp/rss/news/cat6.xml",
    },
    {
        "name": "Reuters Japan Business",
        "url": "https://feeds.reuters.com/reuters/JPBusinessNews",
    },
    {
        "name": "Yahoo Finance Japan",
        "url": "https://news.yahoo.co.jp/rss/topics/business.xml",
    },
    {
        "name": "Nikkei",
        "url": "https://www.nikkei.com/rss/news.rdf",
    },
]


def _strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _parse_rss(xml_text: str, source_name: str) -> list[dict]:
    """Parse RSS XML and return list of news items."""
    items = []
    try:
        root = ET.fromstring(xml_text)

        # Handle both RSS 2.0 and Atom
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # Try RSS 2.0 first
        channel = root.find("channel")
        if channel is None:
            channel = root

        for item in channel.findall("item"):
            title_el = item.find("title")
            desc_el = item.find("description")
            link_el = item.find("link")
            pubdate_el = item.find("pubDate")

            title = _strip_html(title_el.text if title_el is not None else "")
            if not title:
                continue

            summary = _strip_html(desc_el.text if desc_el is not None else "")[:400]
            link = link_el.text.strip() if link_el is not None and link_el.text else None

            published = datetime.utcnow()
            if pubdate_el is not None and pubdate_el.text:
                try:
                    published = parsedate_to_datetime(pubdate_el.text).replace(tzinfo=None)
                except Exception:
                    pass

            items.append({
                "source": source_name,
                "title": title,
                "summary": summary if summary else None,
                "url": link,
                "published_at": published,
            })

    except Exception as e:
        logger.warning(f"RSS parse error for {source_name}: {e}")

    return items[:20]


async def fetch_rss_feed(url: str, source_name: str) -> list[dict]:
    """Fetch and parse a single RSS feed."""
    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 StockAnalysisBot/1.0"},
        ) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return _parse_rss(response.text, source_name)
    except Exception as e:
        logger.warning(f"Failed to fetch RSS from {url}: {e}")
    return []


async def fetch_all_news() -> list[dict]:
    """Fetch news from all RSS feeds concurrently."""
    tasks = [fetch_rss_feed(feed["url"], feed["name"]) for feed in RSS_FEEDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    for result in results:
        if isinstance(result, list):
            all_items.extend(result)

    # Deduplicate by title prefix
    seen = set()
    unique = []
    for item in all_items:
        key = item["title"][:30].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    # Sort by date desc
    unique.sort(key=lambda x: x.get("published_at", datetime.min), reverse=True)
    return unique[:30]


def categorize_news(items: list[dict], holding_codes: list[str]) -> list[dict]:
    """Categorize news items by relevance."""
    for item in items:
        title = item.get("title", "").lower()
        summary = (item.get("summary") or "").lower()
        text = title + " " + summary

        item["relevance"] = "market"
        item["stock_code"] = None

        if any(k in text for k in ["日銀", "fed", "金利", "為替", "円", "経済指標", "gdp", "インフレ", "boj", "fomc"]):
            item["relevance"] = "macro"

    return items
