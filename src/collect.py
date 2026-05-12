"""主流程: 抓取 → AI 處理 → 儲存 JSON → 寄送 Email。"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

from .ai_processor import curate
from .config import DATA_DIR, DOCS_DIR, FINANCE_TICKERS, RSS_SOURCES, load_settings
from .email_sender import send_email
from .fetchers.finance import fetch_dashboard
from .fetchers.github_trending import fetch_github_trending
from .fetchers.hackernews import fetch_hackernews
from .fetchers.rss_fetcher import fetch_rss

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("collect")

TPE_TZ = timezone(timedelta(hours=8))


def _gather() -> tuple[list, list[str]]:
    """抓取所有來源,回傳 (articles, skipped_sources)。"""
    articles = []
    skipped: list[str] = []

    rss_items = fetch_rss(RSS_SOURCES)
    if not rss_items:
        skipped.append("RSS (全部)")
    articles.extend(rss_items)

    try:
        articles.extend(fetch_hackernews())
    except Exception as exc:  # noqa: BLE001
        logger.error("HN 失敗: %s", exc)
        skipped.append("Hacker News")

    try:
        articles.extend(fetch_github_trending())
    except Exception as exc:  # noqa: BLE001
        logger.error("GitHub Trending 失敗: %s", exc)
        skipped.append("GitHub Trending")

    return articles, skipped


def _build_report(today: str, dashboard: dict, curated: dict, skipped: list[str]) -> dict:
    return {
        "date": today,
        "generated_at": datetime.now(TPE_TZ).isoformat(timespec="seconds"),
        "model_version": load_settings().gemini_model,
        "dashboard": dashboard,
        "sections": curated["sections"],
        "anomalies": {
            "skipped_sources": skipped,
            "notes": "" if not skipped else f"今日異常來源: {', '.join(skipped)}",
        },
    }


def _save_json(report: dict) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{report['date']}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("JSON 已寫入 %s", path)
    return path


def _update_pages_index(report: dict) -> None:
    """更新 /docs/data 鏡像 + 日期索引,供 GitHub Pages 載入。"""
    pages_data_dir = DOCS_DIR / "data"
    pages_data_dir.mkdir(parents=True, exist_ok=True)
    target = pages_data_dir / f"{report['date']}.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # 維護日期清單(降冪),供前端日期選單使用
    dates = sorted(
        [p.stem for p in pages_data_dir.glob("*.json") if p.stem != "index"],
        reverse=True,
    )
    (pages_data_dir / "index.json").write_text(
        json.dumps({"latest": dates[0] if dates else "", "dates": dates}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Pages 索引已更新 (%d 筆歷史)", len(dates))


def main() -> int:
    settings = load_settings()
    today = datetime.now(TPE_TZ).strftime("%Y-%m-%d")
    logger.info("=== 開始產製 %s 日報 ===", today)

    articles, skipped = _gather()
    logger.info("候選新聞共 %d 則,異常來源: %s", len(articles), skipped or "無")

    dashboard = fetch_dashboard(FINANCE_TICKERS)
    curated = curate(articles, settings)
    report = _build_report(today, dashboard, curated, skipped)

    _save_json(report)
    _update_pages_index(report)

    try:
        send_email(report, settings)
    except Exception as exc:  # noqa: BLE001
        logger.error("Email 寄送失敗: %s", exc)
        return 2

    logger.info("=== 完成 ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
