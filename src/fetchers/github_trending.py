"""GitHub Trending (Python / TypeScript 中含 AI 關鍵字的專案)。"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from .rss_fetcher import RawArticle

logger = logging.getLogger(__name__)

AI_HINTS = ("ai", "llm", "gpt", "agent", "gemini", "claude", "mcp", "rag", "embedding")


def _fetch_lang(lang: str) -> list[RawArticle]:
    url = f"https://github.com/trending/{lang}?since=daily"
    out: list[RawArticle] = []
    try:
        resp = requests.get(url, headers={"User-Agent": "DailyAIInsights/1.0"}, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for repo in soup.select("article.Box-row"):
            link_el = repo.select_one("h2 a")
            if not link_el:
                continue
            href = link_el.get("href", "").strip()
            repo_name = href.lstrip("/")
            desc_el = repo.select_one("p")
            description = desc_el.get_text(strip=True) if desc_el else ""
            blob = f"{repo_name} {description}".lower()
            if not any(h in blob for h in AI_HINTS):
                continue
            out.append(
                RawArticle(
                    title=f"[{lang}] {repo_name}",
                    url=f"https://github.com{href}",
                    summary=description,
                    source="GitHub Trending",
                    published_at=datetime.now(timezone.utc),
                    weight=0.7,
                )
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("GitHub Trending 失敗 (%s): %s", lang, exc)
    return out


def fetch_github_trending() -> list[RawArticle]:
    items = _fetch_lang("python") + _fetch_lang("typescript")
    logger.info("GitHub Trending 抓取 %d 則", len(items))
    return items
