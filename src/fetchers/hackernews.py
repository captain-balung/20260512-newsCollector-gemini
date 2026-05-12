"""Hacker News (Algolia API): points > 100 且含 AI 關鍵字。"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests

from .rss_fetcher import RawArticle

logger = logging.getLogger(__name__)

ALGOLIA_URL = "https://hn.algolia.com/api/v1/search_by_date"
AI_TAGS = ("ai", "llm", "gpt", "gemini", "claude", "agent", "machine learning")


def fetch_hackernews(min_points: int = 100, hours: int = 24) -> list[RawArticle]:
    results: list[RawArticle] = []
    for tag in AI_TAGS:
        try:
            resp = requests.get(
                ALGOLIA_URL,
                params={
                    "query": tag,
                    "tags": "story",
                    "numericFilters": f"points>{min_points},created_at_i>{int(datetime.now(timezone.utc).timestamp()) - hours * 3600}",
                    "hitsPerPage": 10,
                },
                timeout=15,
            )
            resp.raise_for_status()
            for hit in resp.json().get("hits", []):
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}"
                results.append(
                    RawArticle(
                        title=hit.get("title", ""),
                        url=url,
                        summary=f"HN {hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments",
                        source="Hacker News",
                        published_at=datetime.fromtimestamp(hit["created_at_i"], tz=timezone.utc),
                        weight=0.9,
                    )
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("HN 抓取例外 (tag=%s): %s", tag, exc)
    # 去重 (URL)
    seen: set[str] = set()
    deduped = []
    for art in results:
        if art.url in seen:
            continue
        seen.add(art.url)
        deduped.append(art)
    logger.info("Hacker News 抓取 %d 則 (去重後)", len(deduped))
    return deduped
