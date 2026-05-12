"""全域設定與常數。"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


@dataclass(frozen=True)
class Category:
    id: str
    display: str
    keywords: tuple[str, ...]


CATEGORIES: tuple[Category, ...] = (
    Category(
        "giants_market",
        "🏢 巨頭動向與市場脈動",
        ("google", "openai", "anthropic", "microsoft", "meta", "nvidia", "alphabet", "qqq"),
    ),
    Category(
        "dev_tools_agents",
        "🛠️ 開發者工具與 AI 代理",
        ("agent", "copilot", "cursor", "claude code", "sdk", "framework"),
    ),
    Category(
        "generative_media",
        "🎵 生成式多媒體與創作",
        ("video", "audio", "music", "image", "veo", "sora", "midjourney", "stable diffusion"),
    ),
    Category(
        "edtech_applications",
        "📚 教育科技與應用創新",
        ("education", "edtech", "k-12", "學習", "教學", "課程"),
    ),
    Category(
        "infra_opensource",
        "🧠 底層架構與開源模型",
        ("open source", "huggingface", "llama", "mistral", "embedding", "infrastructure"),
    ),
    Category(
        "law_ethics_society",
        "⚖️ 法律倫理與社會衝擊",
        ("regulation", "policy", "ethics", "lawsuit", "copyright", "倫理", "法規"),
    ),
)


RSS_SOURCES: tuple[dict, ...] = (
    # 巨頭與底層
    {"name": "Google The Keyword", "url": "https://blog.google/rss/", "weight": 1.0},
    {"name": "Google Developers Blog", "url": "https://developers.googleblog.com/feeds/posts/default", "weight": 1.0},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "weight": 1.0},
    {"name": "Anthropic News", "url": "https://www.anthropic.com/news/rss.xml", "weight": 1.0},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "weight": 0.9},
    # 教育科技
    {"name": "EdSurge", "url": "https://www.edsurge.com/articles_rss", "weight": 0.8},
    # 台灣
    {"name": "國科會 NSTC 最新消息", "url": "https://www.nstc.gov.tw/rss/most/ch/realtimenews", "weight": 1.2},
)


FINANCE_TICKERS: tuple[str, ...] = ("QQQ", "GOOGL", "AAPL", "MSFT", "NVDA", "META")


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    smtp_user: str
    smtp_password: str
    email_recipient: str
    email_sender_name: str
    max_gemini_calls: int
    max_tokens: int
    github_pages_url: str


def load_settings() -> Settings:
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        email_recipient=os.getenv("EMAIL_RECIPIENT", "captain.balung@gmail.com"),
        email_sender_name=os.getenv("EMAIL_SENDER_NAME", "Daily AI Insights"),
        max_gemini_calls=int(os.getenv("MAX_GEMINI_CALLS", "50")),
        max_tokens=int(os.getenv("MAX_TOKENS", "200000")),
        github_pages_url=os.getenv("GITHUB_PAGES_URL", ""),
    )
