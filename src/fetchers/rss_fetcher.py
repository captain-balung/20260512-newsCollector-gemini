"""通用 RSS 抓取器。處理過去 24h 內、含 AI 關鍵字的條目。"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

import feedparser

logger = logging.getLogger(__name__)

AI_KEYWORDS = (
    "ai", "artificial intelligence", "llm", "gpt", "gemini", "claude",
    "machine learning", "deep learning", "neural", "transformer",
    "agent", "rag", "embedding", "diffusion", "人工智慧", "人工智能",
    "大模型", "生成式", "教育科技", "edtech",
)


@dataclass
class RawArticle:
    title: str
    url: str
    summary: str
    source: str
    published_at: datetime
    weight: float = 1.0


def _is_recent(published: datetime, hours: int = 24) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return published >= cutoff


def _has_ai_keyword(text: str) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in AI_KEYWORDS)


def _parse_date(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        struct = getattr(entry, key, None) or entry.get(key)
        if struct:
            return datetime(*struct[:6], tzinfo=timezone.utc)
    return None


def fetch_rss(sources: Iterable[dict], lookback_hours: int = 24) -> list[RawArticle]:
    """從多個 RSS 來源抓取近 N 小時內的 AI 相關文章。"""
    results: list[RawArticle] = []
    for src in sources:
        try:
            feed = feedparser.parse(src["url"])
            if feed.bozo and not feed.entries:
                logger.warning("RSS 失敗: %s (%s)", src["name"], feed.bozo_exception)
                continue
            for entry in feed.entries:
                published = _parse_date(entry)
                if not published or not _is_recent(published, lookback_hours):
                    continue
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                blob = f"{title} {summary}"
                # 台灣政府來源不需 AI 關鍵字過濾 (本身已是高訊噪比)
                if src.get("weight", 1.0) < 1.2 and not _has_ai_keyword(blob):
                    continue
                results.append(
                    RawArticle(
                        title=title.strip(),
                        url=entry.get("link", ""),
                        summary=summary[:1000],
                        source=src["name"],
                        published_at=published,
                        weight=src.get("weight", 1.0),
                    )
                )
        except Exception as exc:  # noqa: BLE001 — 單一來源失敗不應中斷
            logger.warning("RSS 例外: %s — %s", src["name"], exc)
    logger.info("RSS 共抓取 %d 則", len(results))
    return results
