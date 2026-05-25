"""
法規向量化腳本
解析 data/laws/law_tuflow.md → ChromaDB（13條）

執行方式（.venv 啟動後）：
    python -m backend.scripts.ingest_laws
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.services.rag_service import ingest_law_markdown
from backend.config import get_settings

settings = get_settings()


def main():
    print("[*] Ingesting law document...")
    print(f"   來源：{settings.law_file_path}")
    print(f"   向量庫：{settings.chroma_db_path}")
    print()

    try:
        result = ingest_law_markdown(settings.law_file_path)
        print(f"\n[OK] Ingest complete!")
        print(f"   Articles: {result['chunks_added']}")
        print(f"   Laws:     {result['laws_parsed']}")
        print(f"\nLaw list:")
        for law in result["laws"]:
            print(f"   - {law}")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Ingest failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
