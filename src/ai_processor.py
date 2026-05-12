"""Gemini AI 處理: 篩選、分類、摘要、專家點評。"""
from __future__ import annotations

import json
import logging
import re
from typing import Iterable

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_fixed

from .config import CATEGORIES, Settings
from .fetchers.rss_fetcher import RawArticle

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """你是「Captain Balung」主編,擅長從每日 AI 產業動態中,以「教育科技、媒體設計、金融市場」三大專業視角進行選稿與點評。

任務:從下方候選新聞中,選出最具決策參考價值的條目,分類至六大面向,並為每則新聞撰寫:
1. 一句話標題(繁體中文,精煉具吸引力)
2. core_summary: 2-3 句話的事件摘要
3. expert_insight: 從「教育科技 / 媒體設計 / 金融市場」其中至少一項視角,提出 1-2 句的專家點評(說明為何值得關注、可能影響)
4. tags: 1-3 個關鍵字標籤(中文)
5. priority: "high" 僅當為「台灣政府動態」或「重大金融變動」時使用,否則為 "normal"

六大面向 (category_id 必須使用以下之一):
- giants_market: 🏢 巨頭動向與市場脈動
- dev_tools_agents: 🛠️ 開發者工具與 AI 代理
- generative_media: 🎵 生成式多媒體與創作
- edtech_applications: 📚 教育科技與應用創新
- infra_opensource: 🧠 底層架構與開源模型
- law_ethics_society: ⚖️ 法律倫理與社會衝擊

每個面向選 2-3 則,若該面向當日無合適新聞,回傳空陣列(主流程會自動補入 fallback 文案)。

僅回傳 JSON,格式:
{
  "sections": [
    {
      "category_id": "giants_market",
      "items": [
        {
          "title": "...",
          "core_summary": "...",
          "expert_insight": "...",
          "source_url": "...",
          "tags": ["..."],
          "priority": "high" | "normal"
        }
      ]
    }
  ]
}

請務必使用候選新聞列表中的 source_url 原值,不可自行編造 URL。"""


FALLBACK_INSIGHTS = {
    "giants_market": "本日各大 AI 巨頭無重大公開動態,可關注下週財報季與模型發布節奏。",
    "dev_tools_agents": "本日開發者生態無新工具突破,Agent 框架仍在 MCP 與長上下文上演進。",
    "generative_media": "本日生成式多媒體領域無重大發表,Veo/Sora 競爭仍在白熱化階段。",
    "edtech_applications": "本日教育科技無新政策或產品上線,K-12 與大專端持續整合 AI 助教。",
    "infra_opensource": "本日開源社群無重大模型釋出,Hugging Face 仍以 Embedding 與小型語言模型為主流。",
    "law_ethics_society": "本日法律倫理面無新監管動態,歐盟 AI Act 與美國各州立法仍在落地中。",
}


def _build_candidate_payload(articles: Iterable[RawArticle], limit: int = 80) -> str:
    """精簡 article 內容以節省 token。"""
    arts = sorted(articles, key=lambda a: (a.weight, a.published_at), reverse=True)[:limit]
    lines = []
    for i, a in enumerate(arts, 1):
        summary = re.sub(r"<[^>]+>", "", a.summary or "")[:300]
        lines.append(
            f"[{i}] 來源={a.source} | 標題={a.title} | URL={a.url} | 摘要={summary}"
        )
    return "\n".join(lines)


def _extract_json(text: str) -> dict:
    """從可能含 markdown code fence 的回應抽出 JSON。"""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("回應中找不到 JSON 物件")
    return json.loads(match.group(0))


@retry(stop=stop_after_attempt(2), wait=wait_fixed(3))
def _call_gemini(model: genai.GenerativeModel, prompt: str) -> dict:
    response = model.generate_content(prompt)
    return _extract_json(response.text)


def curate(articles: list[RawArticle], settings: Settings) -> dict:
    """呼叫 Gemini 進行篩選 + 分類 + 點評,回傳已分組的 sections 結構。"""
    if not settings.gemini_api_key:
        raise RuntimeError("缺少 GEMINI_API_KEY")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        settings.gemini_model,
        system_instruction=SYSTEM_PROMPT,
        generation_config={"response_mime_type": "application/json"},
    )

    if not articles:
        logger.warning("候選新聞為空,全部走 fallback")
        return _empty_sections()

    candidates_blob = _build_candidate_payload(articles)
    prompt = f"以下為今日候選新聞,請依規範選稿並回傳 JSON:\n\n{candidates_blob}"
    try:
        result = _call_gemini(model, prompt)
    except Exception as exc:  # noqa: BLE001
        logger.error("Gemini 呼叫最終失敗: %s", exc)
        return _empty_sections()

    return _normalize_sections(result)


def _empty_sections() -> dict:
    return {
        "sections": [
            {
                "category_id": cat.id,
                "category_display": cat.display,
                "items": [],
                "fallback_note": FALLBACK_INSIGHTS[cat.id],
            }
            for cat in CATEGORIES
        ]
    }


def _normalize_sections(raw: dict) -> dict:
    """補入 category_display 與 fallback_note,確保六大面向都存在。"""
    by_id = {s.get("category_id"): s for s in raw.get("sections", [])}
    normalized = []
    for cat in CATEGORIES:
        sec = by_id.get(cat.id, {"category_id": cat.id, "items": []})
        items = sec.get("items", []) or []
        for it in items:
            it.setdefault("priority", "normal")
            it.setdefault("tags", [])
        normalized.append({
            "category_id": cat.id,
            "category_display": cat.display,
            "items": items,
            "fallback_note": FALLBACK_INSIGHTS[cat.id] if not items else "",
        })
    return {"sections": normalized}
