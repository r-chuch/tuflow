"""
TuFlow 後端 FastAPI 入口
啟動指令（在 .venv 啟動後）：
    uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.config import get_settings
from backend.database import init_db
from backend.routers.match_router import router as match_router
from backend.routers.form_router  import router as form_router
from backend.routers.rag_router   import router as rag_router

settings = get_settings()

# ── FastAPI 應用 ──────────────────────────────────────────────────
app = FastAPI(
    title="TuFlow 土不落 API",
    description="AI 智慧土方循環管理系統後端",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS（允許前端開發伺服器）────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 路由掛載 ──────────────────────────────────────────────────────
app.include_router(match_router)
app.include_router(form_router)
app.include_router(rag_router)

# ── 啟動事件：初始化資料庫 ────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"[OK] TuFlow backend started")
    print(f"   Docs: http://localhost:{settings.backend_port}/docs")


# ── 健康檢查 ─────────────────────────────────────────────────────
@app.get("/health", tags=["系統"])
def health_check():
    return {
        "status": "ok",
        "service": "TuFlow 土不落 API",
        "version": "1.0.0",
    }


# ── 前端靜態檔案（Phase 5 建置後啟用）────────────────────────────
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
