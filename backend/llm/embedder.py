"""
sentence-transformers 嵌入模型封裝
使用 paraphrase-multilingual-mpnet-base-v2（支援繁體中文）
模型於首次使用時自動下載至 ~/.cache/
"""
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import numpy as np


MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    """延遲載入模型（只載入一次）"""
    print(f"[*] Loading embedding model: {MODEL_NAME} (first run downloads model...)")
    model = SentenceTransformer(MODEL_NAME)
    print("[OK] Embedding model loaded")
    return model


def encode(text: str | list[str], normalize: bool = True) -> np.ndarray:
    """
    將文字轉換為嵌入向量

    Args:
        text:       單一字串或字串清單
        normalize:  是否 L2 正規化（提升餘弦相似度計算效率）

    Returns:
        np.ndarray: shape (768,) 或 (n, 768)
    """
    model = _load_model()
    return model.encode(text, normalize_embeddings=normalize, show_progress_bar=False)


def embed_query(text: str) -> list[float]:
    """查詢向量（用於 ChromaDB 查詢）"""
    return encode(text).tolist()


def embed_batch(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """批次嵌入（用於文件向量化）"""
    model = _load_model()
    vecs = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return vecs.tolist()
