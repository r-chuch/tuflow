"""
法規問答資料模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class LawRef(BaseModel):
    law_name:     str
    article_num:  str
    excerpt:      Optional[str] = None
    citation_key: Optional[str] = None
    article_type: Optional[str] = None
    authority:    Optional[str] = None


class RAGSource(BaseModel):
    """ChromaDB 實際檢索到的原始條文段落（顯示在引用方框展開後）"""
    law_name:     str
    article_num:  str
    full_text:    str              # 完整條文原文（去除【】標頭後的純內容）
    article_type: Optional[str] = None
    authority:    Optional[str] = None
    similarity:   Optional[float] = None  # 語意相似度 0.0~1.0


class RAGQuery(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    top_k:    int = Field(default=5, ge=1, le=10)


class RAGResponse(BaseModel):
    answer:           str
    law_refs:         list[LawRef]    = []
    sources:          list[RAGSource] = []   # ChromaDB 實際檢索到的條文（新增）
    confidence:       Literal["high", "medium", "low"] = "medium"
    suggested_action: Optional[str] = None
    session_id:       Optional[str] = None


class IngestRequest(BaseModel):
    filepath: str = Field(default="./data/laws/law_tuflow.md")


class RAGStatus(BaseModel):
    doc_count:   int
    laws_loaded: list[str]
    model:       str
    chroma_path: str
