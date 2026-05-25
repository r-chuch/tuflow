"""
法規問答 API 路由
/api/rag/*
"""
from fastapi import APIRouter, HTTPException

from backend.models.rag import RAGQuery, RAGResponse, IngestRequest, RAGStatus
from backend.services.rag_service import query, ingest_law_markdown, get_status

router = APIRouter(prefix="/api/rag", tags=["法規問答"])


# ── 法規查詢 ──────────────────────────────────────────────────────
@router.post("/query", response_model=RAGResponse, summary="法規問答查詢")
def api_rag_query(payload: RAGQuery):
    try:
        return query(payload.question, payload.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"GROQ_API_KEY 未設定：{e}")


# ── 法規資料庫狀態 ────────────────────────────────────────────────
@router.get("/status", summary="法規資料庫狀態")
def api_rag_status():
    return get_status()


# ── 向量化法規文件（管理員）─────────────────────────────────────
@router.post("/ingest", summary="向量化法規 Markdown 文件")
def api_rag_ingest(payload: IngestRequest):
    try:
        return ingest_law_markdown(payload.filepath)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
