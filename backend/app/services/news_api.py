"""
News API integration – fetch related articles for a claim.
Uses NewsAPI.org v2/everything endpoint.
"""
import logging
import re
from typing import List, Dict, Optional

import httpx

from app.utils.config import settings

logger = logging.getLogger(__name__)

NEWS_API_BASE = "https://newsapi.org/v2/everything"


def _query_from_text(text: str, max_words: int = 8) -> str:
    """Build a short search query from claim text (strip punctuation, take key words)."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower()).strip()
    words = [w for w in cleaned.split() if len(w) > 2][:max_words]
    return " ".join(words) if words else text[:100]


async def fetch_related_articles(
    claim_text: str,
    page_size: int = 5,
) -> List[Dict]:
    """
    Fetch articles related to the claim from News API.

    Returns list of dicts: title, url, source, description, publishedAt.
    """
    api_key = settings.NEWSAPI_KEY
    if not api_key or (isinstance(api_key, str) and api_key.startswith("your_")):
        logger.debug("News API key not configured, skipping related articles")
        return []

    query = _query_from_text(claim_text)
    if not query:
        return []

    params = {
        "q": query[:500],
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": min(page_size, 10),
        "apiKey": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(NEWS_API_BASE, params=params)
        if resp.status_code != 200:
            logger.warning("News API returned status %s", resp.status_code)
            return []

        data = resp.json()
        if data.get("status") != "ok":
            logger.warning("News API error: %s", data.get("message", "unknown"))
            return []

        articles = data.get("articles") or []
        out = []
        for a in articles[:page_size]:
            if not a.get("title") or a.get("title") == "[Removed]":
                continue
            out.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "source": (a.get("source") or {}).get("name", "Unknown"),
                "description": (a.get("description") or "")[:200],
                "publishedAt": a.get("publishedAt"),
            })
        logger.info("Fetched %d related articles for claim", len(out))
        return out
    except httpx.TimeoutException:
        logger.warning("News API request timed out")
        return []
    except Exception as e:
        logger.warning("News API error: %s", e)
        return []
