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


class RAGQuery(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    top_k:    int = Field(default=5, ge=1, le=10)


class RAGResponse(BaseModel):
    answer:           str
    law_refs:         list[LawRef] = []
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
