# Daily AI Insights

> AI 產業每日決策情報 — 由 **Captain Balung** 主編、Gemini 2.5 Pro 全自動產製,結合「教育科技、媒體設計、金融市場」三大視角。

## 系統流程

```
GitHub Actions (每日 09:00 UTC+8)
  └─> 抓取 RSS / Hacker News / GitHub Trending / yfinance
       └─> Gemini 2.5 Pro 篩選 + 分類 + 專家點評
            └─> 寫入 data/YYYY-MM-DD.json + docs/data/
                 ├─> GitHub Pages 自動更新門戶網站
                 └─> SMTP 寄送 HTML + 純文字雙版本 Email
```

## 一次性設定

### 1. GitHub Secrets

到 `Settings → Secrets and variables → Actions → Secrets` 新增:

| Secret | 說明 |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio 取得 ([連結](https://aistudio.google.com/app/apikey)) |
| `SMTP_USER` | 寄件 Gmail 地址 |
| `SMTP_PASSWORD` | Gmail App Password ([如何產生](https://myaccount.google.com/apppasswords)) |

### 2. GitHub Variables (可選)

到 `Settings → Secrets and variables → Actions → Variables`:

| Variable | 預設值 |
|---|---|
| `GEMINI_MODEL` | `gemini-2.5-pro` |
| `EMAIL_RECIPIENT` | `captain.balung@gmail.com` |
| `EMAIL_SENDER_NAME` | `Daily AI Insights` |
| `GITHUB_PAGES_URL` | 你的 GitHub Pages URL |
| `MAX_GEMINI_CALLS` | `50` |
| `MAX_TOKENS` | `200000` |

### 3. 啟用 GitHub Pages

`Settings → Pages → Source` 選 **Deploy from a branch**,Branch 選 `main` / `/docs`。

### 4. 手動觸發測試

`Actions → Daily AI Insights → Run workflow`,確認:
- ✅ `data/YYYY-MM-DD.json` 已產生
- ✅ Email 已收到
- ✅ Pages 網站可開啟

## 本機開發

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env  # 填入 API Key
python -m src.collect
```

預覽前端:

```bash
cd docs && python -m http.server 8000
# 開啟 http://localhost:8000
```

## 專案結構

```
.
├── .github/workflows/daily-collect.yml   # 每日 Cron
├── src/
│   ├── collect.py                        # 主流程
│   ├── config.py                         # 來源 / 分類 / Settings
│   ├── ai_processor.py                   # Gemini 整合
│   ├── email_sender.py                   # SMTP + MIME
│   ├── fetchers/
│   │   ├── rss_fetcher.py
│   │   ├── hackernews.py
│   │   ├── github_trending.py
│   │   └── finance.py
│   └── templates/
│       ├── email_html.j2
│       └── email_text.j2
├── data/                                 # 歷史 JSON 主檔
├── docs/                                 # GitHub Pages
│   ├── index.html
│   ├── app.js
│   └── data/                             # 鏡像 + index.json
├── requirement.md
└── README.md
```

## 故障排除

| 症狀 | 排查方向 |
|---|---|
| Workflow 失敗開了 Issue | 點開 Actions → 該次 run → 看 logs 找關鍵字 |
| Email 沒收到 | 確認 Gmail App Password (非一般密碼)、檢查垃圾信匣 |
| Gemini 回傳格式錯誤 | 已內建 2 次重試 + fallback 文案,可改 `src/ai_processor.py` 的 prompt |
| Pages 沒更新 | 確認 Pages source 指向 `main/docs`,且 workflow 有 push commit |

## 驗收項目 (對應 requirement.md §7)

- [ ] 每日 09:00 ±5 分鐘內 Email 寄達
- [ ] 新聞均來自過去 24 小時
- [ ] Gmail Web / App / Outlook / Apple Mail 顯示正常
- [ ] Pages 日期選單動態切換不刷新整頁
- [ ] 每則新聞有教育科技 / 媒體設計 / 金融市場視角的點評
- [ ] Light / Dark Mode 跟隨系統
- [ ] 失敗自動開 Issue
