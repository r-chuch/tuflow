"""
RAG 法規問答服務
1. parse_law_markdown()   — 解析 law_tuflow.md → chunks
2. ingest_to_chroma()     — 向量化並存入 ChromaDB
3. query()                — 語意檢索 + Groq LLM 生成回答
"""
import uuid
import re
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import get_settings
from backend.llm.embedder import embed_query, embed_batch
from backend.llm.wrapper import chat_json
from backend.llm.prompts import RAG_SYSTEM, rag_query_user
from backend.models.rag import LawRef, RAGSource, RAGResponse
from backend.database import get_connection

_settings = get_settings()

# ─── ChromaDB 客戶端（單例）──────────────────────────────────────
_chroma_client: Optional[chromadb.Client] = None


def _get_chroma():
    global _chroma_client
    if _chroma_client is None:
        Path(_settings.chroma_db_path).mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=_settings.chroma_db_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


def _get_collection():
    return _get_chroma().get_or_create_collection(
        name="tuflow_laws",
        metadata={"hnsw:space": "cosine"},
    )


# ─── Markdown 解析器 ──────────────────────────────────────────────
def parse_law_markdown(filepath: str) -> list[dict]:
    """
    解析 law_tuflow.md，回傳 chunks 清單。
    每個 chunk = 一條條文 + metadata。
    """
    chunks = []
    current_law     = None
    current_article = None
    content_lines   = []

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            if line.startswith("## "):         # 法規名稱
                if current_article and content_lines:
                    chunks.append(_build_chunk(
                        current_law, current_article,
                        "\n".join(content_lines).strip()
                    ))
                current_law     = line[3:].strip()
                current_article = None
                content_lines   = []

            elif line.startswith("### "):      # 條文編號
                if current_article and content_lines:
                    chunks.append(_build_chunk(
                        current_law, current_article,
                        "\n".join(content_lines).strip()
                    ))
                current_article = line[4:].strip()
                content_lines   = []

            elif line == "---":                # 法規分隔線，略過
                pass

            else:                              # 條文內容
                if current_article:
                    content_lines.append(line)

    # 最後一條
    if current_article and content_lines:
        chunks.append(_build_chunk(
            current_law, current_article,
            "\n".join(content_lines).strip()
        ))

    return chunks


def _build_chunk(law_name: str, article_num: str, content: str) -> dict:
    return {
        "text": f"【{law_name} {article_num}】\n{content}",
        "metadata": {
            "law_name":     law_name,
            "article_num":  article_num,
            "source_file":  "law_tuflow.md",
            "article_type": _classify_article(content),
            "authority":    _get_authority(law_name),
            "citation_key": f"{law_name}_{article_num}",
        },
    }


def _classify_article(content: str) -> str:
    if any(k in content for k in ["罰鍰", "有期徒刑", "罰金", "違反", "處以"]):
        return "penalty"
    elif any(k in content for k in ["申報", "備查", "許可", "核定", "辦理"]):
        return "procedure"
    elif any(k in content for k in ["應", "不得", "得", "義務"]):
        return "obligation"
    return "general"


def _get_authority(law_name: str) -> str:
    return "local" if "桃園市" in law_name else "central"


# ─── 向量化並存入 ChromaDB ────────────────────────────────────────
def ingest_law_markdown(filepath: Optional[str] = None) -> dict:
    """解析 law_tuflow.md 並向量化所有條文存入 ChromaDB"""
    filepath = filepath or _settings.law_file_path
    if not Path(filepath).exists():
        raise FileNotFoundError(f"法規文件不存在：{filepath}")

    chunks     = parse_law_markdown(filepath)
    collection = _get_collection()

    # 清除舊資料（重新向量化）
    try:
        existing = collection.get()
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    # 批次嵌入
    texts = [c["text"] for c in chunks]
    embeddings = embed_batch(texts)

    ids = [f"law_{i:04d}" for i in range(len(chunks))]
    metadatas = [c["metadata"] for c in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    # 收集法規名稱統計
    laws = list({c["metadata"]["law_name"] for c in chunks})
    print(f"[OK] Ingested {len(chunks)} articles ({len(laws)} laws) -> ChromaDB")

    return {
        "chunks_added": len(chunks),
        "laws_parsed":  len(laws),
        "laws":         laws,
    }


# ─── RAG 查詢 ────────────────────────────────────────────────────
def query(question: str, top_k: int = 5) -> RAGResponse:
    """
    1. 向量化問題
    2. ChromaDB Top-K 語意檢索
    3. 組裝 context → Groq LLM 生成回答
    """
    collection = _get_collection()

    # 檢查資料庫是否有資料
    count = collection.count()
    if count == 0:
        raise RuntimeError(
            "法規資料庫尚未建置。\n"
            "請執行：python -m backend.scripts.ingest_laws"
        )

    # 向量查詢
    q_vec = embed_query(question)
    results = collection.query(
        query_embeddings=[q_vec],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    # 組裝 context
    context = "\n\n".join(docs)

    # 呼叫 LLM
    user_msg = rag_query_user(context, question)
    llm_result = chat_json(RAG_SYSTEM, user_msg, temperature=0.1)

    # 解析 law_refs
    raw_refs = llm_result.get("law_refs", [])
    law_refs = [
        LawRef(
            law_name    = r.get("law_name", ""),
            article_num = r.get("article_num") or r.get("article", ""),
            excerpt     = r.get("excerpt"),
            citation_key= r.get("citation_key"),
            article_type= r.get("article_type"),
            authority   = r.get("authority"),
        )
        for r in raw_refs
    ]

    # 建立 sources：ChromaDB 實際檢索到的原始條文段落
    sources = []
    for doc, meta, dist in zip(docs, metas, distances):
        # 去除【法規名稱 條文號】標頭，只保留純條文內容
        if "\n" in doc:
            full_text = doc.split("\n", 1)[1].strip()
        else:
            full_text = doc.strip()
        sources.append(RAGSource(
            law_name    = meta.get("law_name", ""),
            article_num = meta.get("article_num", ""),
            full_text   = full_text,
            article_type= meta.get("article_type"),
            authority   = meta.get("authority"),
            similarity  = round(1.0 - dist, 3),  # cosine distance → similarity
        ))

    # 存入問答記錄
    import json
    session_id = str(uuid.uuid4())
    conn = get_connection()
    conn.execute("""
        INSERT INTO qa_sessions (id, question, answer, law_refs, confidence)
        VALUES (?,?,?,?,?)
    """, (
        session_id, question,
        llm_result.get("answer", ""),
        json.dumps([r.model_dump() for r in law_refs], ensure_ascii=False),
        llm_result.get("confidence", "medium"),
    ))
    conn.commit()
    conn.close()

    return RAGResponse(
        answer           = llm_result.get("answer", ""),
        law_refs         = law_refs,
        sources          = sources,
        confidence       = llm_result.get("confidence", "medium"),
        suggested_action = llm_result.get("suggested_action"),
        session_id       = session_id,
    )


# ─── 狀態查詢 ────────────────────────────────────────────────────
def get_status() -> dict:
    """取得 ChromaDB 目前狀態"""
    try:
        collection = _get_collection()
        count      = collection.count()

        # 取得已載入的法規名稱
        if count > 0:
            all_metas  = collection.get(include=["metadatas"])["metadatas"]
            laws_loaded = list({m["law_name"] for m in all_metas})
        else:
            laws_loaded = []

        return {
            "doc_count":    count,
            "laws_loaded":  laws_loaded,
            "embed_model":  "paraphrase-multilingual-mpnet-base-v2",  # 向量化／檢索用
            "llm_model":    _settings.groq_model,                     # 答案生成用
            "model":        "paraphrase-multilingual-mpnet-base-v2",   # 向下相容
            "chroma_path":  _settings.chroma_db_path,
        }
    except Exception as e:
        return {
            "doc_count":   0,
            "laws_loaded": [],
            "embed_model": "未載入",
            "llm_model":   _settings.groq_model,
            "model":       "未載入",
            "chroma_path": _settings.chroma_db_path,
            "error":       str(e),
        }
