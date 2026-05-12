"""Email 寄送: SMTP + MIME multipart/alternative。"""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import TEMPLATE_DIR, Settings

logger = logging.getLogger(__name__)


def _render(report: dict, pages_url: str) -> tuple[str, str]:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    ctx = {
        "date": report["date"],
        "dashboard": report.get("dashboard", {}),
        "sections": report.get("sections", []),
        "pages_url": pages_url,
    }
    html = env.get_template("email_html.j2").render(**ctx)
    text = env.get_template("email_text.j2").render(**ctx)
    return html, text


def send_email(report: dict, settings: Settings) -> None:
    if not settings.smtp_user or not settings.smtp_password:
        raise RuntimeError("缺少 SMTP_USER / SMTP_PASSWORD")

    html, text = _render(report, settings.github_pages_url)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Daily AI Insights] {report['date']} 產業情報"
    msg["From"] = formataddr((settings.email_sender_name, settings.smtp_user))
    msg["To"] = settings.email_recipient
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_user, [settings.email_recipient], msg.as_string())
    logger.info("Email 已寄出至 %s", settings.email_recipient)
