import os
from datetime import datetime, timezone

import httpx

from app.database import query


NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_URL = "https://newsapi.org/v2/everything"


def sync_news_for_stock(stock_id: int, ticker: str) -> int:
    """
    Fetch recent stock-related news and store it in market_news.

    If NEWS_API_KEY is not configured, the function safely returns 0.
    """

    if not NEWS_API_KEY:
        return 0

    symbol = ticker.replace(".NS", "").replace(".BO", "")

    params = {
        "q": symbol,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = httpx.get(
            NEWS_API_URL,
            params=params,
            timeout=15,
        )
        response.raise_for_status()

        payload = response.json()

        if payload.get("status") != "ok":
            return 0

        articles = payload.get("articles", [])

        inserted = 0

        for article in articles:
            headline = article.get("title")

            if not headline:
                continue

            source = (
                article.get("source", {}).get("name")
                if article.get("source")
                else None
            )

            url = article.get("url")

            published_at = article.get("publishedAt")

            if published_at:
                try:
                    published_at = datetime.fromisoformat(
                        published_at.replace("Z", "+00:00")
                    ).replace(tzinfo=None)
                except ValueError:
                    published_at = None

            # Avoid duplicate URLs
            existing = query(
                """
                SELECT 1
                FROM market_news
                WHERE stock_id=%s AND url=%s
                LIMIT 1
                """,
                (stock_id, url),
                fetch=True,
            )

            if existing:
                continue

            query(
                """
                INSERT INTO market_news
                (
                    stock_id,
                    headline,
                    source,
                    url,
                    published_at
                )
                VALUES (%s,%s,%s,%s,%s)
                """,
                (
                    stock_id,
                    headline,
                    source,
                    url,
                    published_at,
                ),
            )

            inserted += 1

        return inserted

    except Exception:
        return 0