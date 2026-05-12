# 軟體需求說明書 (Requirement.md)

## 1. 專案概述
* **專案名稱：** AI 產業每日決策情報 (Daily AI Insights)
* **主編代號：** Captain Balung
* **專案願景：** 打造一個全自動化、具備深度觀點且視覺精美的 AI 產業情報系統。透過 AI Agent 每日抓取全球動態，並結合「教育科技、媒體設計、金融市場」等專業視角進行過濾、分類與專家點評。
* **核心價值：** * 轉化資訊碎片為專業決策參考。
    * 建立具備個人品牌特質的數位知識資產（GitHub 存檔）。

## 2. 系統架構
本系統採用 **Serverless (GitHub Actions)** 開發架構，確保零維護成本與高自動化運作：
1. **資料抓取層：** 每日定時觸發，透過 API (如 Tavily, RSS) 檢索過去 24 小時新聞。
2. **AI 處理層：** 呼叫 Gemini 1.5 Pro 進行新聞篩選、自動分類、撰寫核心摘要及專家點評。
3. **資料持久層：** 產出結構化 JSON 檔案並儲存於 GitHub `/data` 資料夾作為歷史資料庫。
4. **多端發布層：** * **Web：** 更新 GitHub Pages 門戶網站內容。
    * **Email：** 同時寄送互動版 (HTML) 與靜態版 (Plain Text/Static) 郵件。

## 3. 功能需求

### 3.1 資訊過濾與指定資料來源 (Target Sources)
為確保資訊品質與高訊噪比，AI 爬蟲需優先針對以下權威節點進行檢索與訂閱 (RSS/API)：

* **巨頭與底層技術：**
    * Google The Keyword Blog & Google AI Developer Blog (追蹤 Gemini 與開源工具)。
    * OpenAI Blog & Anthropic News (模型更新)。
    * Hugging Face Daily Papers & Blog (開源模型、Embedding、STT 技術)。
* **開發者與生態系：**
    * Hacker News (演算法篩選 `points > 100` 且含 AI 關鍵字)。
    * GitHub Trending (Python / TypeScript 區塊的 AI 專案)。
* **教育科技與社會政策：**
    * EdSurge / 相關 EdTech 權威媒體 (K-12 教育科技應用)。
    * **台灣專屬來源：** 國科會 (NSTC) 最新消息 RSS、原住民族委員會公告 (追蹤本土語料庫與 AI 指引)。
* **金融與市場表現：**
    * Yahoo Finance API 或 RSS (追蹤 QQQ, GOOGL, AAPL 等標的之重大 AI 相關異動)。

### 3.2 選稿邏輯與分類
* **六大核心面向：**
    1. **🏢 巨頭動向與市場脈動**
    2. **🛠️ 開發者工具與 AI 代理**
    3. **🎵 生成式多媒體與創作**
    4. **📚 教育科技與應用創新**
    5. **🧠 底層架構與開源模型**
    6. **⚖️ 法律倫理與社會衝擊**
* **內容規格：** 每個面向需包含 2-3 則精選新聞。
* **重點強化：** 特別偵測「台灣政府動態」與「重大金融變動」並於標題下方加入特殊權重標記。

### 3.3 郵件派送系統 (Email Delivery)
* **寄送時間：** 每日早上 09:00 (UTC+8)。
* **多重替代內容 (MIME Multipart/Alternative)：**
    * **互動版本 (Interactive HTML)：** 使用 `<details>` 與 `<summary>` 標籤實現摺疊式卡片，支援點擊展開詳情。
    * **靜態版本 (Static Fallback)：** 全展開式 HTML 或 Markdown 格式，確保在 Jasper 或舊式客戶端仍能完整閱讀。
* **內容三層結構：**
    1. 標題層：類別圖示 + 一句話標題。
    2. 詳細層：核心摘要 + 專家點評（以專業視角分析意義）。
    3. 來源層：附上原始新聞 URL 連結。

### 3.4 門戶網站與存檔 (Portal & Archive)
* **託管平台：** GitHub Pages。
* **首頁功能：** 自動渲染當日最新的日報內容。
* **歷史存檔：** 提供日期選單，可檢索並載入過去生成的 JSON 檔案，無需刷新頁面即可查看歷史情報。
* **SEO 與檢索：** 支援透過標籤過濾（如：點擊「教育科技」標籤顯示歷史相關摘要）。

## 4. 視覺與美術規範 (UI/UX)
* **設計風格：** 現代極簡科技感 (Modern Minimalist Tech) 混合職人精神。
* **配色方案：**
    * **主色 (Primary)：** 深海軍藍 `#1A2B3C` (探索者形象)。
    * **強調色 (Accent)：** 警示紅 `#E63946` (Kiai 氣勢感)。
    * **輔助色：** 背景極淺灰 `#F8F9FA`、金融綠 `#2A9D8F`、政策橙 `#F4A261`。
* **排版特色：** * 頂部顯示「今日看板」匯總金融與市場指標。
    * 卡片式設計，區塊間使用清晰的 Emoji 引導。
    * 符合黑暗模式 (Dark Mode) 優化。

## 5. 技術堆棧 (Tech Stack)
* **語言/腳本：** Python 3.x
* **AI 大模型：** Gemini 1.5 Pro (Google AI Studio)
* **自動化：** GitHub Actions (Cron Job)
* **前端技術：** Vanilla JS + Tailwind CSS (極簡化託管於 GitHub Pages)
* **傳輸協議：** SMTP (Gmail) 或 SendGrid API

## 6. 資料結構範例 (data/YYYY-MM-DD.json)

```json
{
  "date": "2026-05-12",
  "dashboard": { "qqq_index": "+1.2%", "alphabet": "Stable" },
  "sections": [
    {
      "category": "EdTech & Applications",
      "items": [
        {
          "title": "台灣發布教育 AI 倫理指引",
          "summary": "國科會與原民會聯合發布...",
          "insight": "這代表未來開發族語保存工具時需更重視數據主權...",
          "source_url": "https://...",
          "tags": ["台灣政府", "語言保存"]
        }
      ]
    }
  ]
}
```

## 7. 驗收標準 (Acceptance Criteria)
1. 每日 09:00 前完成 GitHub Data 更新與 Email 寄送。
2. Email 內容在手機與桌機版 Gmail 顯示正常且摺疊功能可用。
3. GitHub Pages 能夠正確載入 `/data` 資料夾內的歷史 JSON 檔案。
4. 每則新聞必須包含針對「教育科技、媒體設計或金融市場」的專家點評。