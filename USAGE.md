# TuFlow 土不落 — 使用說明手冊

> **AI 智慧土方循環管理系統** | 桃園市營建廢土 AI 媒合平台  
> 版本：v1.0 | 更新日期：2026-05-26

---

## 目錄

1. [系統概覽](#系統概覽)
2. [環境需求](#環境需求)
3. [首次安裝設定](#首次安裝設定)
4. [啟動系統](#啟動系統)
5. [功能模組操作說明](#功能模組操作說明)
   - [法規問答（AI Chat）](#一法規問答ai-chat)
   - [智慧媒合（地圖媒合）](#二智慧媒合地圖媒合)
   - [自動填單（電子聯單）](#三自動填單電子聯單)
6. [API 端點總覽](#api-端點總覽)
7. [管理員操作](#管理員操作)
8. [常見問題排解](#常見問題排解)
9. [系統架構摘要](#系統架構摘要)

---

## 系統概覽

TuFlow 土不落是一套整合三大 AI 模組的土方循環管理系統，解決台灣營建業每年 **3,600～4,200 萬立方公尺**廢土的供需失衡問題。

| 模組 | 路由 | 核心功能 |
|------|------|----------|
| 🤖 法規問答 | `/chat` | 以自然語言查詢土方相關法規，回應附法條引用 |
| 🗺️ 智慧媒合 | `/map`  | AI 計算供需評分，地圖視覺化最佳清運路線 |
| 📋 自動填單 | `/manifest` | 語音或文字一句話自動填完電子聯單並匯出 PDF |

---

## 環境需求

### 後端
| 工具 | 最低版本 | 說明 |
|------|----------|------|
| Python | 3.11+ | 已測試 3.11.x |
| pip | 24.0+ | 建議在 `.venv` 內使用 |
| Groq API 金鑰 | — | 從 [console.groq.com](https://console.groq.com) 免費取得 |

### 前端
| 工具 | 最低版本 | 說明 |
|------|----------|------|
| Node.js | 20.0+ | 已測試 24.12.0 |
| npm | 10.0+ | 已測試 11.6.2 |

### 瀏覽器
- **語音輸入功能**：需使用 **Google Chrome 或 Microsoft Edge**（Web Speech API 支援）
- 其他功能：所有現代瀏覽器皆可

---

## 首次安裝設定

> 💡 若已完成安裝，可直接跳至「[啟動系統](#啟動系統)」

### 步驟 1：建立 Python 虛擬環境

```powershell
# 在專案根目錄執行
cd d:\ai_project\tuflow

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

> ⚠️ 安裝 `sentence-transformers`、`chromadb` 需要較長時間（約 5～10 分鐘，含大型 ML 模型下載）

### 步驟 2：設定 API 金鑰

```powershell
# 複製範本
Copy-Item .env.example .env
```

用文字編輯器開啟 `.env`，填入您的 Groq API 金鑰：

```env
GROQ_API_KEY=gsk_your_actual_key_here
```

> 💡 前往 [https://console.groq.com](https://console.groq.com) → API Keys → Create API Key

### 步驟 3：初始化資料庫與示範資料

```powershell
# 確保在虛擬環境中（.venv）
$env:PYTHONIOENCODING = "utf-8"

# 初始化 SQLite 資料庫（建立 4 張表格）
python -c "from backend.database import init_db; init_db()"

# 匯入示範工地資料（8 個桃園工地、3 筆媒合、3 張聯單）
python -m backend.scripts.seed_demo_data
```

### 步驟 4：向量化法規文件

```powershell
# 將 5 部法規 12 條文向量化存入 ChromaDB
python -m backend.scripts.ingest_laws
```

預期輸出：
```
[*] Ingesting law document...
[OK] Ingested 12 articles (5 laws) -> ChromaDB
```

### 步驟 5：安裝前端相依套件

```powershell
cd frontend
npm install
cd ..
```

---

## 啟動系統

### 方法 A：使用一鍵啟動腳本（推薦）

開啟兩個 PowerShell 視窗：

**視窗 1 — 後端**
```powershell
cd d:\ai_project\tuflow
.\start_backend.ps1
```

**視窗 2 — 前端**
```powershell
cd d:\ai_project\tuflow
.\start_frontend.ps1
```

### 方法 B：手動啟動

**後端（PowerShell 視窗 1）**
```powershell
cd d:\ai_project\tuflow
.venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING = "utf-8"
uvicorn backend.main:app --reload --port 8001
```

**前端（PowerShell 視窗 2）**
```powershell
cd d:\ai_project\tuflow\frontend
npm run dev
```

### 確認啟動成功

| 服務 | 網址 | 確認方式 |
|------|------|----------|
| 前端介面 | http://localhost:5173 | 開啟瀏覽器，應看到 TuFlow 深綠色首頁 |
| 後端 API | http://localhost:8001/health | 瀏覽器應顯示 `{"status":"ok"}` |
| API 文件 | http://localhost:8001/docs | Swagger UI 互動式文件 |

---

## 功能模組操作說明

### 一、法規問答（AI Chat）

**路徑**：http://localhost:5173/chat

#### 基本使用

1. 開啟法規問答頁面
2. 在底部輸入框輸入您的問題（繁體中文）
3. 按 **Enter** 或點擊 **送出** 按鈕
4. AI 回應通常在 2～5 秒內出現，附有：
   - 詳細法規解釋
   - 引用的法條（法規名稱 + 條號 + 原文摘錄）
   - 建議下一步行動

#### 快速提示詞

介面提供 4 個預設快速問題按鈕：
- 「電子聯單怎麼申報？」
- 「土方違規的罰則是什麼？」
- 「桃園市土方自治條例重點？」
- 「土資場設置需要哪些許可？」

#### 範例問法

```
問：桃園市的土方電子聯單要在幾天內申報？
問：違法棄土最重處罰是什麼？
問：第一類與第二類土石方有何差異？
問：工地辦理完工後，剩餘土方應如何處理？
```

#### 離線模式（無 GROQ_API_KEY）

若 API 金鑰未設定，系統自動切換為 **Demo 模式**，顯示預先準備的示範問答（`public/demo_qa.json`），適合展示用途。

---

### 二、智慧媒合（地圖媒合）

**路徑**：http://localhost:5173/map

#### 使用流程

**Step 1：選擇供方工地**
- 頁面左側顯示所有「供方（有土方可輸出）」工地清單
- 點擊工地卡片，地圖會以紅色標記顯示該工地位置

**Step 2：執行媒合**
- 選定供方工地後，點擊 **「開始 AI 媒合」** 按鈕
- 系統在 1～3 秒內計算最佳媒合方案
- 地圖上會顯示供方（紅色）和需方（綠色）標記，並畫出路線

**Step 3：查看評分結果**
- 右側或下方面板顯示媒合結果清單
- 每筆結果包含：

| 欄位 | 說明 |
|------|------|
| 工地名稱 | 需方（土方接收方）工地 |
| 距離 | 從供方到需方的直線距離（km） |
| 總分 | 0～100 分，越高越優先 |
| 距離分數 | 佔 40%，距離越近越高 |
| 數量分數 | 佔 35%，供需體積匹配度 |
| 相容分數 | 佔 25%，土質類型相容程度 |

#### 評分說明

```
總分 = 0.40 × 距離分數 + 0.35 × 數量分數 + 0.25 × 土質相容分數

距離分數：
  ≤  5 km → 100 分
  ≤ 10 km → 100 - (距離 - 5) × 8
  ≤ 20 km → 60  - (距離 - 10) × 4
  ≤ 40 km → 20  - (距離 - 20) × 1
  > 40 km → 0 分

土質相容矩陣（供方 → 需方）：
  第一類 → 第一類：100 分
  第一類 → 第二類：80 分
  第一類 → 第三類：40 分
  第二類 → 第一類：30 分
  第二類 → 第二類：100 分
  第二類 → 第三類：60 分
  第三類 → 第一類：0 分
  第三類 → 第二類：20 分
  第三類 → 第三類：100 分
```

#### 示範資料

系統預載 **8 個桃園地區工地**：
- 供方（有土方）：3 個工地
- 需方（需要填土）：3 個工地
- 土資場（收容場所）：2 個工地

---

### 三、自動填單（電子聯單）

**路徑**：http://localhost:5173/manifest

#### 使用流程

**Step 1：輸入工程描述**

有兩種輸入方式：

**文字輸入**
- 在文字輸入框直接打字，描述此次出土的相關資訊

**語音輸入（需 Chrome 或 Edge）**
- 點擊麥克風按鈕開始錄音
- 清楚說出工程資訊（同文字輸入格式）
- 系統自動將語音轉為文字

**Step 2：AI 提取欄位**

點擊 **「AI 分析填入」** 後，系統從您的描述中自動提取：

| 欄位類型 | 欄位名稱 | 說明 |
|----------|----------|------|
| B 類（AI 提取）| 出場路線 | 車輛離場路線名稱 |
| B 類（AI 提取）| 實際出土量 | 本次出土體積（立方公尺）|
| B 類（AI 提取）| 駕駛人姓名 | 司機姓名 |
| B 類（AI 提取）| 駕駛人身份證 | 格式：英文字母 + 9 位數字 |
| B 類（AI 提取）| 車頭車號 | 格式：XX-9999 或 XXX-9999 |
| B 類（AI 提取）| 車斗車號 | 格式：XX-9999 或 XXX-9999 |

**Step 3：確認並修正**

- 已提取的欄位以綠色標示，信心度顯示為百分比
- 未能提取的欄位標示為「⚠ 需補填」
- 可直接點擊欄位進行人工修正

**Step 4：建立聯單**

點擊 **「建立電子聯單」** 後：
- 系統自動產生聯單序號（格式：`出土流向編號-收容場所代碼-土質代碼-流水號`）
- 產生聯單 ID（格式：`TY-YYYYMMDDHHMMSS-XXXX`）

**Step 5：匯出 PDF**

點擊 **「匯出 PDF」**，下載包含 A 類（系統欄位）和 B 類（運載資訊）的完整電子聯單。

#### 語音輸入範例

```
「路線一，今天出土十二點五方，
駕駛是王大明，身份證 A123456789，
車頭車號 KAA-1234，車斗 KAA-5678」
```

AI 將自動解析為：
- 出場路線：路線一
- 實際出土量：12.5 m³
- 駕駛人姓名：王大明
- 駕駛人身份證：A123456789
- 車頭車號：KAA-1234
- 車斗車號：KAA-5678

#### 欄位驗證規則

| 欄位 | 格式要求 |
|------|----------|
| 身份證字號 | 1 英文字母（大寫）+ 1 或 2 + 8 位數字，如 `A123456789` |
| 車號（車頭/車斗）| 2～3 英文字母 + 連字號 + 4 位數字，如 `KAA-1234` |
| 出土量 | 數字，範圍 0.1～30.0 立方公尺 |

---

## API 端點總覽

### 法規問答 `/api/rag`

| 方法 | 端點 | 說明 |
|------|------|------|
| `POST` | `/api/rag/query` | 法規問答查詢 |
| `GET` | `/api/rag/status` | 法規資料庫狀態 |
| `POST` | `/api/rag/ingest` | 向量化法規文件（管理員） |

**查詢範例**
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "電子聯單申報期限是幾天？", "top_k": 5}'
```

**回應格式**
```json
{
  "answer": "依桃園市自治條例第12條規定...",
  "law_refs": [
    {
      "law_name": "桃園市營建剩餘土石方管理自治條例",
      "article": "第12條",
      "excerpt": "...應於出場後XX日內..."
    }
  ],
  "confidence": "high",
  "suggested_action": "建議前往桃園市政府工務局辦理申報"
}
```

### 智慧媒合 `/api/match`

| 方法 | 端點 | 說明 |
|------|------|------|
| `GET` | `/api/match/sites` | 取得工地列表 |
| `POST` | `/api/match/sites` | 新增工地 |
| `POST` | `/api/match/run` | 執行媒合計算 |
| `PATCH` | `/api/match/matches/{id}` | 更新媒合狀態 |
| `GET` | `/api/match/demo` | 取得 Demo 資料 |

**媒合請求範例**
```bash
curl -X POST http://localhost:8000/api/match/run \
  -H "Content-Type: application/json" \
  -d '{
    "supply_id": "site-001",
    "max_results": 5,
    "filters": {"max_distance_km": 30}
  }'
```

### 自動填單 `/api/form`

| 方法 | 端點 | 說明 |
|------|------|------|
| `POST` | `/api/form/extract` | AI 提取 B 類欄位 |
| `POST` | `/api/form/create` | 建立電子聯單 |
| `PATCH` | `/api/form/manifests/{id}` | 更新聯單欄位 |
| `GET` | `/api/form/manifests/{id}` | 取得聯單詳情 |
| `POST` | `/api/form/manifests/{id}/export-pdf` | 匯出 PDF |
| `GET` | `/api/form/demo` | 取得 Demo 聯單資料 |

**欄位提取範例**
```bash
curl -X POST http://localhost:8000/api/form/extract \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "路線一，12.5方，王大明，A123456789，車號KAA-1234"}'
```

---

## 管理員操作

### 重新向量化法規文件

若需更新法規內容，修改 `data/laws/law_tuflow.md` 後執行：

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING = "utf-8"
python -m backend.scripts.ingest_laws
```

或透過 API：

```bash
curl -X POST http://localhost:8000/api/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{"filepath": "./data/laws/law_tuflow.md"}'
```

### 重新匯入示範資料

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING = "utf-8"
python -m backend.scripts.seed_demo_data
```

### 查看法規資料庫狀態

```bash
curl http://localhost:8000/api/rag/status
# 回應：{"doc_count": 12, "laws_loaded": 5, "model": "paraphrase-multilingual-mpnet-base-v2"}
```

### 新增工地資料（API）

```bash
curl -X POST http://localhost:8000/api/match/sites \
  -H "Content-Type: application/json" \
  -d '{
    "role": "supply",
    "name": "龜山區新建工程",
    "address": "桃園市龜山區○○路○○號",
    "lat": 25.035,
    "lng": 121.368,
    "soil_type": "class1",
    "volume_m3": 500,
    "price_per_m3": 150
  }'
```

---

## 常見問題排解

### 問題 1：後端啟動失敗 — `GROQ_API_KEY 未設定`

**原因**：`.env` 檔案不存在或 API 金鑰未填寫。

**解決**：
```powershell
# 確認 .env 存在
Test-Path .env

# 若不存在，複製範本
Copy-Item .env.example .env

# 編輯 .env，填入 GROQ_API_KEY
notepad .env
```

---

### 問題 2：法規問答返回「法規資料庫尚未建置」

**原因**：ChromaDB 尚未完成法規向量化。

**解決**：
```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING = "utf-8"
python -m backend.scripts.ingest_laws
```

---

### 問題 3：前端顯示「連線失敗，切換 Demo 模式」

**原因**：後端未啟動，前端自動切換到離線 Demo 模式（顯示預設資料）。

**解決**：確認後端已在 port 8000 啟動：
```powershell
# 確認後端健康狀態
Invoke-RestMethod http://localhost:8000/health
```

---

### 問題 4：語音輸入無法使用

**原因**：Web Speech API 需要 HTTPS 或 localhost，且只支援 Chrome/Edge。

**解決**：
1. 使用 **Google Chrome** 或 **Microsoft Edge** 開啟 http://localhost:5173/manifest
2. 若瀏覽器要求麥克風權限，點擊「允許」
3. 確認麥克風裝置已正確連接

---

### 問題 5：PDF 匯出失敗

**原因**：reportlab CID 字體載入問題（偶發）。

**解決**：重新啟動後端，再試一次。若問題持續：
```powershell
pip install --upgrade reportlab
```

---

### 問題 6：Windows 編碼錯誤（UnicodeEncodeError）

**原因**：Windows 繁體中文系統預設 cp950 編碼與部分字元不相容。

**解決**：啟動後端前設定環境變數：
```powershell
$env:PYTHONIOENCODING = "utf-8"
uvicorn backend.main:app --reload --port 8000
```

---

### 問題 7：`chromadb` 或 `sentence-transformers` 無法匯入

**原因**：大型 ML 套件安裝失敗或未完成。

**解決**：
```powershell
.venv\Scripts\Activate.ps1
pip install chromadb sentence-transformers --timeout 300
```

> ⚠️ `sentence-transformers` 需下載約 1GB 的模型，請確保網路穩定並耐心等待。

---

## 系統架構摘要

```
瀏覽器 (localhost:5173)
  │  React + Vite + Tailwind CSS
  │  Leaflet.js 地圖 / Web Speech API 語音
  │
  │  Vite Proxy → /api/* → localhost:8000
  │
FastAPI 後端 (localhost:8000)
  ├── /api/rag/*    ← ChromaDB + Groq LLM (RAG 法規問答)
  ├── /api/match/*  ← 評分演算法 + geopy 距離計算
  └── /api/form/*   ← Groq LLM 欄位提取 + reportlab PDF
  │
  ├── SQLite (data/tuflow.db)
  │     sites / matches / manifests / qa_sessions
  │
  └── ChromaDB (data/chroma_db/)
        collection: tuflow_laws (12 法條, 5 部法規)
```

---

## 競賽演示腳本

以下為 5 步驟完整展示流程（約 5 分鐘）：

| 步驟 | 操作 | 預期結果 |
|------|------|----------|
| 1 | 開啟 http://localhost:5173 | 深綠色首頁，3 個功能卡 |
| 2 | 點選「法規問答」→ 問「桃園土方電子聯單怎麼申報？」| AI 回應含法條引用，3 秒內完成 |
| 3 | 點選「智慧媒合」→ 選供方工地 → 點「開始 AI 媒合」| 地圖顯示媒合結果與評分 |
| 4 | 點選「電子聯單」→ 語音輸入或輸入工程描述 | 欄位自動填入，信心度標示 |
| 5 | 點「建立聯單」→ 點「匯出 PDF」| 下載完整格式電子聯單 PDF |

---

*本文件由 TuFlow 開發團隊維護 | 如有問題請參閱 [PROGRESS.md](PROGRESS.md) 或 [PLAN.md](PLAN.md)*
