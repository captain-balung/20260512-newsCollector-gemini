"""金融市場指標 (yfinance)。"""
from __future__ import annotations

import logging

import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_dashboard(tickers: tuple[str, ...]) -> dict[str, str]:
    """回傳 {ticker: "+1.23%" 或 "Stable"} 的儀表板資料。"""
    dashboard: dict[str, str] = {}
    for ticker in tickers:
        try:
            hist = yf.Ticker(ticker).history(period="2d")
            if len(hist) < 2:
                dashboard[ticker] = "N/A"
                continue
            prev_close = float(hist["Close"].iloc[-2])
            last_close = float(hist["Close"].iloc[-1])
            pct = (last_close - prev_close) / prev_close * 100
            if abs(pct) < 0.3:
                dashboard[ticker] = "Stable"
            else:
                dashboard[ticker] = f"{pct:+.2f}%"
        except Exception as exc:  # noqa: BLE001
            logger.warning("yfinance 失敗 %s: %s", ticker, exc)
            dashboard[ticker] = "N/A"
    return dashboard
