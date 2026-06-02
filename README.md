<div align="center">

# TuFlow 土不落

### AI 智慧土方循環管理系統

*Intelligent Construction Soil Circular Management Platform*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Llama--3.3--70B-F55036?style=flat-square)](https://console.groq.com)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-FF6F00?style=flat-square)](https://www.trychroma.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> 2026 全國大專院校永續 × 循環經濟 × AI 創新提案競賽 參賽作品

</div>

---

## 目錄

1. [專案概覽](#1-專案概覽)
2. [核心問題與解決方案](#2-核心問題與解決方案)
3. [功能模組](#3-功能模組)
4. [系統架構](#4-系統架構)
5. [技術選型](#5-技術選型)
6. [API 規格](#6-api-規格)
7. [快速開始](#7-快速開始)
8. [環境設定](#8-環境設定)
9. [資料管理](#9-資料管理)
10. [演算法設計](#10-演算法設計)
11. [專案結構](#11-專案結構)
12. [開發指南](#12-開發指南)
13. [預期效益](#13-預期效益)
14. [永續發展指標](#14-永續發展指標)

---

## 1. 專案概覽

TuFlow 土不落是一套以 **AI 驅動的去中心化虛擬調度平台**，解決台灣每年 **3,600〜4,200 萬立方公尺**（約 6,900 萬噸）營建剩餘土石方的去化困境。

系統整合三大 AI 模組，實現從「被動管末稽查」到「主動源頭賦能」的典範轉移：

| 模組 | 技術核心 | 量化目標 |
|------|----------|----------|
| ⬡ **法規問答 RAG** | LLM + ChromaDB 語意檢索 | 法規查詢時間縮短 **70%** |
| ◉ **智慧媒合** | 多維評分演算法 + 地理計算 | 媒合效率提升 **70%**，清運成本降低 **15〜30%** |
| ▦ **自動填單** | NLP 資訊抽取 + 語音輸入 | 行政作業錯誤率降低 **80%** |

---

## 2. 核心問題與解決方案

### 2.1 問題背景

2026 年台灣土方清運新制全面上路，GPS 追蹤與電子聯單制度雖提升管理透明度，卻在轉換期間引發系統性失靈：

```
供給端：合法土資場容量飽和，廢土去化無門
需求端：B 工地急需回填原料，卻不知何處取得
資訊端：供需資訊分散，媒合依靠人脈電話，效率極低
合規端：電子聯單複雜，人工填寫耗時且易出錯
```

**核心洞察**：A 工地挖出的土方，正是 B 工地急需的回填原料。資源已存在，缺乏的是智慧調度系統。

### 2.2 解決策略對比

| 面向 | 現行方式（管末稽查）| TuFlow（源頭賦能）|
|------|-------------------|-----------------|
| **運作模式** | 依賴實體土資場中繼暫存，容量易飽和 | 去中心化平台，促成工地對工地直接媒合 |
| **資訊流動** | 靜態公告欄，需人工查詢 | AI 動態運算，即時推薦最佳配對 |
| **管理邏輯** | 將第一線人員視為潛在違規者 | 降低合法作業的時間與金錢門檻 |
| **核心價值** | 廢棄物清運與防弊 | 資源封閉迴圈，實踐循環經濟 |

---

## 3. 功能模組

### 3.1 法規問答（RAG Legal Q&A）

採用 **Retrieval-Augmented Generation（RAG）** 架構，確保每一條回覆都有法條依據，杜絕 LLM 幻覺風險。

**Pipeline 流程：**

```
法規 PDF/MD 文件
  │
  ▼ Recursive Chunking（400 tokens，重疊 60 tokens）
  │  + Metadata 注入（法規名稱、條號、效力層級、來源頁碼）
  │
  ▼ Embedding（multilingual-mpnet-base-v2，本機執行）
  │
  ▼ ChromaDB 向量資料庫（餘弦相似度索引）
  │
  ▼ 使用者提問 → 語意向量化 → Top-K 檢索
  │
  ▼ Context 組裝 → Groq LLM（JSON Mode）
  │
  ▼ 結構化回覆：{ answer, law_refs[], confidence, suggested_action }
```

**已涵蓋法規（初始版本）：**
- 營建剩餘土石方處理方案
- 桃園市剩餘土石方管理自治條例
- 廢棄物清理法（土方相關條文）
- 水土保持法
- 土石方資源堆置場設置管理辦法

**前端特色：**
- 法條引用卡片可展開顯示完整原文（含餘弦相似度分數）
- 區分 LLM 摘錄與 ChromaDB 完整原文
- 信心度分級（high / medium / low）顯示

### 3.2 智慧媒合（Smart Matching）

基於多維評分演算法，綜合距離、數量匹配度、土質相容性三大維度，提供最佳媒合排序。

**評分公式：**

```
Total Score = 0.40 × S_distance + 0.35 × S_quantity + 0.25 × S_compat
```

詳見 [演算法設計](#10-演算法設計)。

**前端特色：**
- Leaflet 互動地圖，紅色圓點（供方）/ 綠色圓點（需方）/ 琥珀圓點（土資場）
- 最佳媒合路線以紅色實線標示，其餘以虛線顯示
- MatchCard 顯示分項評分進度條
- 效益統計面板（配對數、最近距離、最高評分）

### 3.3 自動填單（Automated Form Filling）

支援語音與文字雙模式輸入，透過 LLM 語意分析自動提取電子聯單 B 類欄位。

**處理流程：**

```
語音輸入（Web Speech API）→ 文字轉錄
     │
     ▼
文字輸入 → Groq LLM（Prompt Engineering + JSON Mode）
     │
     ▼ 提取欄位：出場路線、實際出土量、駕駛姓名、身份證、車頭/車斗車號
     │
     ▼ 格式驗證（Pydantic）：身份證格式、車牌格式、數量範圍
     │
     ▼ SQLite 寫入 → 聯單序號生成（TY-YYYYMMDDHHMMSS-XXXX）
     │
     ▼ PDF 匯出（ReportLab，支援繁體中文）
```

**備援機制：** Groq API 不可用時自動降級為正則表達式解析，確保核心功能不中斷。

---

## 4. 系統架構

```
┌─────────────────────────────────────────────────────────────────┐
│                    瀏覽器前端（React 18 + Vite）                  │
│                                                                  │
│   / 首頁    /chat 法規問答    /map 智慧媒合    /manifest 填單      |
│                                                                 │
│   React Router  │  React-Leaflet  │  Web Speech API  │  Fetch   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP（Vite Proxy → /api）
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend（Port 8001）                       │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ /api/rag/*  │  │/api/match/* │  │ /api/form/* │             │
│  │  RAG Router │  │Match Router │  │ Form Router │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                    │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐             │
│  │ RAG Service │  │Match Service│  │Form Service │             │
│  │ ChromaDB    │  │Geo + Score  │  │NLP Extract  │             │
│  │ Embedder    │  │Compat Matrix│  │PDF Export   │             │
│  └──────┬──────┘  └─────────────┘  └─────────────┘             │
│         │                                                      │
│  ┌──────▼──────────────────────────────────┐                   │
│  │         LLM Wrapper（Groq SDK）           │                  │
│  │   llama-3.3-70b-versatile（Q&A + Form）  │                   │
│  └─────────────────────────────────────────┘                   │
└──────┬──────────────────────────┬──────────────────────────────┘
       │                          │
  ┌────▼──────┐            ┌──────▼──────┐
  │ ChromaDB  │            │   SQLite    │
  │ 法規向量庫 │            │  tuflow.db  │
  │ ~100 條文 │            │  5 張資料表  │
  └───────────┘            └─────────────┘
```

### 資料流向

```
使用者操作          前端元件            API 端點              後端服務
────────────────────────────────────────────────────────────────────
問法規問題    →   ChatScene.jsx   →  POST /api/rag/query  →  rag_service.query()
選供方工地    →   MapScene.jsx    →  POST /api/match/run  →  match_service.run_matching()
語音填單      →  ManifestScene   →  POST /api/form/extract→  form_service.extract_fields()
匯出 PDF      →  ManifestScene   →  GET  /api/form/../pdf →  form_service.export_manifest_pdf()
```

---

## 5. 技術選型

| 層次 | 技術 | 版本 | 選擇理由 |
|------|------|------|----------|
| **後端框架** | FastAPI | ≥ 0.111 | asyncio 原生支援；Pydantic 自動驗證；自動產生 OpenAPI 文件 |
| **資料庫** | SQLite | 內建 |
| **向量資料庫** | ChromaDB | ≥ 0.5 | 本機模式，無需雲端帳號；法規文件量小，離線可用 |
| **嵌入模型** | paraphrase-multilingual-mpnet-base-v2 | sentence-transformers | 本機執行，繁體中文語意支援優異；768 維向量 |
| **LLM** | Groq API（llama-3.3-70b-versatile）| ≥ 0.9 | 推論速度 ~500 tok/s；OpenAI 相容介面 |
| **PDF 匯出** | ReportLab | ≥ 4.0 | 純 Python，無 GTK 系統依賴；支援 CID 中文字體 |
| **前端框架** | React 18 + Vite | - | HMR 快速開發；模組化元件架構 |
| **地圖** | React-Leaflet | - | 輕量；OpenStreetMap 免費圖磚；圓點標記易於自訂 |
| **語音輸入** | Web Speech API | 瀏覽器原生 | 零部署成本；Chrome 原生支援 |
| **地理計算** | geopy（geodesic）| ≥ 2.4 | WGS-84 橢球面精確距離，比 Haversine 誤差更小 |

---

## 6. API 規格

後端啟動後可於 `http://localhost:8001/docs` 查閱完整 Swagger UI，或 `/redoc` 查閱 ReDoc 格式文件。

### 智慧媒合 `/api/match`

```
GET    /api/match/sites              取得所有工地列表（可篩選 role / soil_type）
POST   /api/match/sites              新增工地（供方 / 需方 / 土資場）
POST   /api/match/run                執行 AI 媒合
PATCH  /api/match/matches/{id}       更新媒合狀態（proposed → confirmed）
GET    /api/match/matches            取得媒合記錄
GET    /api/match/demo               取得 Demo 工地資料
```

**POST /api/match/run 範例：**

```json
// Request
{
  "supply_id": "site-001",
  "max_results": 5,
  "filters": { "max_distance_km": 50 }
}

// Response
{
  "matches": [
    {
      "site_id": "site-003",
      "name": "八德區公園填方工程",
      "distance_km": 5.70,
      "score": 81.43,
      "score_breakdown": {
        "distance": 83.6,
        "quantity": 75.0,
        "compat": 100.0
      },
      "volume_available": 1200,
      "price_per_m3": 350
    }
  ]
}
```

### 法規問答 `/api/rag`

```
POST   /api/rag/query                語意問答（含法條引用）
GET    /api/rag/status               RAG 資料庫狀態查詢
POST   /api/rag/ingest               上傳法規文件向量化（管理員）
```

**POST /api/rag/query 範例：**

```json
// Request
{ "question": "在山坡地堆置土石方需要什麼許可？", "top_k": 5 }

// Response
{
  "answer": "依水土保持法第 12 條規定，在山坡地從事堆置土石...",
  "law_refs": [
    {
      "law_name": "水土保持法",
      "article": "第 12 條",
      "article_type": "obligation",
      "authority": "central",
      "excerpt": "山坡地之開發利用..."
    }
  ],
  "sources": [
    {
      "law_name": "水土保持法",
      "article_num": "第 12 條",
      "full_text": "山坡地之開發利用，應實施水土保持之處理與維護...",
      "similarity": 0.923
    }
  ],
  "confidence": "high",
  "suggested_action": "向縣市政府水土保持主管機關申請許可"
}
```

### 自動填單 `/api/form`

```
POST   /api/form/extract             NLP 提取 B 類欄位
POST   /api/form/create              建立電子聯單
PATCH  /api/form/manifests/{id}      更新聯單欄位
GET    /api/form/manifests/{id}      查詢聯單詳情
GET    /api/form/manifests/{id}/export-pdf  匯出 PDF
GET    /api/form/demo                Demo 聯單資料
```

### 系統

```
GET    /health                       健康狀態檢查
GET    /docs                         Swagger UI
GET    /redoc                        ReDoc 文件
```

---

## 7. 快速開始

### 前置需求

| 工具 | 版本 | 安裝方式 |
|------|------|----------|
| Python | 3.10+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Groq API Key | — | [console.groq.com](https://console.groq.com)（免費） |

### 一鍵啟動（Windows PowerShell）

```powershell
# 1. 複製此專案
git clone https://github.com/your-org/tuflow.git
cd tuflow

# 2. 建立 Python 虛擬環境並安裝後端套件
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. 設定環境變數
Copy-Item .env.example .env
# 編輯 .env，填入 GROQ_API_KEY（必填）

# 4. 初始化資料庫並載入 Demo 資料
python -m backend.database
python -m backend.scripts.seed_demo_data

# 5. 向量化法規文件
python -m backend.scripts.ingest_laws

# 6. 啟動後端（Terminal 1）
uvicorn backend.main:app --reload --port 8001

# 7. 安裝並啟動前端（Terminal 2）
cd frontend
npm install
npm run dev
```

開啟瀏覽器訪問 **http://localhost:5173**

---

## 8. 環境設定

複製 `.env.example` 為 `.env` 並填入以下設定：

```ini
# ─── 必填 ─────────────────────────────────────────────────────────
GROQ_API_KEY=gsk_your_api_key_here      # 至 console.groq.com 免費申請

# ─── LLM 模型 ─────────────────────────────────────────────────────
GROQ_MODEL=llama-3.3-70b-versatile      # 主力模型（Q&A + 填單提取）
GROQ_MODEL_FAST=llama-3.1-8b-instant    # 快速模型（備用）

# ─── 路徑設定（可保持預設）────────────────────────────────────────
DATABASE_URL=sqlite:///./data/tuflow.db
CHROMA_DB_PATH=./data/chroma_db
LAW_FILE_PATH=./data/laws/law_tuflow.md
DEMO_DATA_PATH=./data/demo

# ─── 網路設定 ────────────────────────────────────────────────────
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8001
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

> ⚠️ **安全提醒**：`.env` 已列入 `.gitignore`，請勿將真實 API 金鑰提交至版本控制。

---

## 9. 資料管理

### SQLite 資料庫結構（`data/tuflow.db`）

```sql
-- 工地資料（供方 / 需方 / 土資場）
sites (id, role, name, address, lat, lng, soil_code, volume_m3,
       price_per_m3, contact, created_at)

-- 媒合記錄
matches (id, supply_site_id, demand_site_id, volume_matched,
         distance_km, score_total, score_distance, score_quantity,
         score_compat, status, matched_at)

-- 電子聯單
manifests (id, manifest_number, project_name, project_code,
           disposal_site_code, disposal_site_name, soil_code,
           total_volume_m3, route_list, manifest_status,
           route_name, actual_volume_m3, driver_name, driver_id,
           truck_head_plate, truck_body_plate, raw_input,
           match_id, status, created_at)

-- 法規問答記錄
qa_sessions (id, question, answer, law_refs, created_at)
```

### Demo 資料集

```
data/demo/
├── sites.json        # 8 個桃園地區工地（供方 × 3、需方 × 3、土資場 × 2）
├── matches.json      # 3 筆示範媒合記錄
├── manifests.json    # 3 筆示範電子聯單
└── qa.json           # 4 筆示範問答（離線備援）
```

### 管理指令

```powershell
# 重新植入 Demo 工地資料
python -m backend.scripts.seed_demo_data

# 重新向量化法規（修改法規文件後執行）
python -m backend.scripts.ingest_laws

# 查詢 RAG 向量庫狀態
curl http://localhost:8001/api/rag/status
```

---

## 10. 演算法設計

### 10.1 媒合評分公式

```
Total Score = 0.40 × S_distance + 0.35 × S_quantity + 0.25 × S_compat
```

### 10.2 距離分數（S_distance）

使用 geopy geodesic 計算 WGS-84 橢球面距離：

```python
距離 d (km)    →    距離分數
─────────────────────────────
d ≤  5 km      →  100 分
d ≤ 10 km      →  100 - (d - 5)  × 8    # 線性遞減至 60
d ≤ 20 km      →   60 - (d - 10) × 4    # 線性遞減至 20
d ≤ 40 km      →   20 - (d - 20) × 1    # 線性遞減至  0
d  > 40 km     →    0 分（超出可接受範圍）
```

### 10.3 數量匹配分數（S_quantity）

```python
ratio = min(supply_vol, demand_vol) / max(supply_vol, demand_vol)
S_quantity = ratio × 100
```

### 10.4 土質相容矩陣（S_compat）

```
              需方接受土質
              class1  class2  class3
供方提供 ┌─────────────────────────────
class1   │  100      80      40
class2   │   30     100      60
class3   │    0      20     100
```

- `class1`：第一類（天然土，適用範圍廣）
- `class2`：第二類（混合土，部分受限）
- `class3`：第三類（改良土，僅適用特定場合）

### 10.5 媒合驗證結果（Demo 資料）

```
供方：桃園中山路新建大樓工程（class1，2,000 m³）

排名  需方                     距離      總分    分項（距 / 量 / 相容）
────────────────────────────────────────────────────────────────────
#1   龜山工業區停車場整地      4.95 km   91.11   100.0 / 83.3 / 100.0
#2   八德區公園填方工程        5.70 km   81.43    83.6 / 75.0 / 100.0
#3   平鎮工業區道路整平工程    9.53 km   76.75    60.0 / 71.4 / 100.0
```

---

## 11. 專案結構

```
tuflow/
│
├── README.md                   # 本文件
├── USAGE.md                    # 詳細操作說明
├── PLAN.md                     # 完整系統規劃
├── PROGRESS.md                 # 實作進度記錄
├── CLAUDE.md                   # 開發準則（Claude AI 協作指引）
│
├── .env.example                # 環境變數範本（複製並填入金鑰）
├── .gitignore                  # 排除 .env / *.db / chroma_db / .venv
├── requirements.txt            # Python 依賴套件
│
├── backend/                    # FastAPI 後端
│   ├── main.py                 # 應用入口、CORS、路由掛載
│   ├── config.py               # BaseSettings 讀取 .env（lru_cache）
│   ├── database.py             # SQLite 建表、init_db()
│   │
│   ├── routers/                # API 路由層（薄層，僅負責 HTTP 介面）
│   │   ├── match_router.py     # /api/match/*
│   │   ├── form_router.py      # /api/form/*
│   │   └── rag_router.py       # /api/rag/*
│   │
│   ├── services/               # 業務邏輯層
│   │   ├── geo_service.py      # geodesic 距離計算、距離評分
│   │   ├── match_service.py    # 媒合演算法、評分公式、相容矩陣
│   │   ├── form_service.py     # 欄位提取、聯單建立、PDF 匯出
│   │   └── rag_service.py      # ChromaDB 索引、語意檢索、RAG 問答
│   │
│   ├── llm/                    # AI 模型層
│   │   ├── wrapper.py          # Groq SDK 統一介面（JSON Mode）
│   │   ├── prompts.py          # Prompt Template（填單提取 + 法規問答）
│   │   └── embedder.py         # sentence-transformers 封裝
│   │
│   ├── models/                 # Pydantic 資料模型
│   │   ├── site.py             # Site、SoilRecord
│   │   ├── match.py            # MatchRequest、MatchResult
│   │   ├── form.py             # SystemFields、ExtractedFields、ManifestCreate
│   │   └── rag.py              # RAGQuery、RAGResponse、RAGSource
│   │
│   ├── scripts/
│   │   ├── seed_demo_data.py   # 植入桃園地區 8 個 Demo 工地
│   │   └── ingest_laws.py      # CLI 批次向量化法規文件
│   │
│   └── tests/
│       ├── test_match.py       # 媒合演算法單元測試
│       ├── test_form.py        # 填單提取單元測試
│       └── test_rag.py         # RAG Pipeline 單元測試
│
├── frontend/                   # React 前端（Vite）
│   ├── vite.config.js          # Vite 設定（Proxy /api → :8001）
│   ├── index.html              # HTML 入口
│   │
│   ├── src/
│   │   ├── main.jsx            # React 應用掛載點
│   │   ├── App.jsx             # React Router 路由定義
│   │   ├── index.css           # 深綠主題 CSS Variables
│   │   │
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   └── Navbar.jsx
│   │   │   ├── Home/
│   │   │   │   └── HeroSection.jsx
│   │   │   ├── Matching/
│   │   │   │   ├── MapScene.jsx     # 媒合主場景
│   │   │   │   ├── LeafletMap.jsx   # Leaflet 地圖元件
│   │   │   │   └── MatchCard.jsx    # 媒合結果卡片
│   │   │   ├── LegalQA/
│   │   │   │   ├── ChatScene.jsx    # 問答主場景
│   │   │   │   ├── ChatMessage.jsx  # 訊息氣泡
│   │   │   │   └── LawCitation.jsx  # 法條引用（可展開）
│   │   │   └── Manifest/
│   │   │       ├── ManifestScene.jsx # 填單主場景
│   │   │       └── VoiceInput.jsx    # 語音輸入按鈕
│   │   │
│   │   └── services/
│   │       └── api.js           # fetch wrapper（matchApi / formApi / ragApi）
│   │
│   └── public/
│       └── demo_qa.json         # 離線備援問答資料
│
└── data/
    ├── laws/
    │   └── law_tuflow.md        # 法規文件（5 法規 / 13 條文）
    ├── demo/                    # Demo JSON 資料集
    │   ├── sites.json
    │   ├── matches.json
    │   ├── manifests.json
    │   └── qa.json
    ├── chroma_db/               # ChromaDB 向量資料庫（git ignore）
    └── tuflow.db                # SQLite 資料庫（git ignore）
```

---

## 12. 開發指南

### 12.1 本地開發環境

```powershell
# 啟動後端（熱重載）
.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8001

# 啟動前端（HMR）
cd frontend
npm run dev

# 執行後端測試
cd tuflow
pytest backend/tests/ -v

# 建置前端生產版本
cd frontend
npm run build
# 建置後 frontend/dist/ 會自動被後端靜態服務掛載
```

### 12.2 Prompt 設計規範

**填單提取 Prompt（`llm/prompts.py`）：**
- System：強制 JSON 輸出格式、欄位名稱、值域範圍（車號格式、體積 0.1〜30 m³）
- User：注入可選路線清單，引導模型做選擇而非自由發揮
- 解析：Pydantic 驗證後若格式不符，自動降級至正則備援

**法規問答 Prompt：**
- System：嚴格限制「僅能根據提供的法規片段回答，不得捏造」
- JSON 強制格式：`{ answer, law_refs[], confidence, suggested_action }`
- 使用 Groq `response_format={"type": "json_object"}` 確保輸出可解析

### 12.3 新增法規文件

1. 將 Markdown 格式法規放入 `data/laws/`
2. 更新 `LAW_FILE_PATH` 或直接合併至 `law_tuflow.md`
3. 重新執行向量化：

```powershell
python -m backend.scripts.ingest_laws
```

### 12.4 注意事項

| 項目 | 說明 |
|------|------|
| `lru_cache` 行為 | `get_settings()` 在程序啟動時快取。修改 `.env` 後需重啟後端才能生效。 |
| React 保留 prop | `ref` / `key` 是 React 保留屬性，不可作為自訂 prop 名稱（會靜默失敗）。 |
| Windows 編碼 | 後端 `print()` 使用 ASCII 避免 cp950 編碼錯誤。 |
| 語音輸入 | Web Speech API 需 HTTPS 或 localhost，建議使用 Chrome。 |
| ChromaDB 首次啟動 | 第一次 import sentence-transformers 會下載模型（約 400MB），需耐心等待。 |

---

## 13. 預期效益

| 面向 | 量化目標 | 質化目標 |
|------|----------|----------|
| **作業效率** | 法規查詢時間 ↓ 70%；行政填單效率 ↑ 80% | 降低使用門檻，提升合規意願 |
| **資源媒合** | 供需媒合效率 ↑ 70% | 促進政策落地，縮短制度銜接落差 |
| **運輸成本** | 運輸距離 ↓ 20〜40%；清運成本 ↓ 15〜30% | 推動產業數位轉型 |
| **違規風險** | 人為錯誤 ↓ 80%；非法棄置行為 ↓ 30〜50% | 強化環境治理，保護第一線從業者 |
| **環境效益** | 碳排放 ↓ 15〜25%；土方再利用率 ↑ 70〜80% | 實踐循環經濟，降低廢棄物壓力 |

---

## 14. 永續發展指標

本系統對應聯合國永續發展目標（SDGs）與 ESG 三大面向：

```
SDG 11 — 永續城鄉：提升營建系統效率，減少資源浪費與環境污染
SDG 12 — 責任消費及生產：促進土方與營建資源的循環利用
SDG 13 — 氣候行動：降低運輸與作業過程中的碳排放

E（環境）：最佳化運輸路徑 → 減碳；促進再利用 → 循環經濟
S（社會）：穩定房價結構；保障第一線司機工作權益；居住正義
G（治理）：數據化管理；法規遵循輔助；可追蹤的資料管理系統
```

---

<div align="center">

**TuFlow 土不落** — 讓土方從廢棄物變成可流通的資源

*從「管末稽查」到「源頭賦能」，重新定義台灣營建廢土的價值*

---

競賽參加:

© 2026 TuFlow Team · 2026 全國大專院校永續 × 循環經濟 × AI 創新提案競賽

### 團隊成員:

劉若英/國立中央大學/電機工程學系/114521122

陳士杰/國立中央大學/企業管理學系/110401030

塗玟荇/國立中央大學/文學院學士班/111108006

張峪銓/國立中央大學/資訊工程學系/112502514


</div>
