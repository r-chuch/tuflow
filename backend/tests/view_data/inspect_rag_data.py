"""
檢視 RAG 法規資料：解析後的 chunks + ChromaDB 儲存狀態
"""
import sys
sys.path.insert(0, ".")

from backend.services.rag_service import parse_law_markdown, _get_collection
from backend.config import get_settings

settings = get_settings()

# ── 1. 解析 Markdown → Chunks ─────────────────────────────────────
print("=" * 70)
print("  RAG 法規資料檢視工具")
print("=" * 70)

chunks = parse_law_markdown(settings.law_file_path)
print(f"\n[解析結果] 共 {len(chunks)} 個 chunks，來源：{settings.law_file_path}\n")

# 統計
laws = {}
types = {}
auths = {}
for c in chunks:
    m = c["metadata"]
    laws[m["law_name"]] = laws.get(m["law_name"], 0) + 1
    types[m["article_type"]] = types.get(m["article_type"], 0) + 1
    auths[m["authority"]] = auths.get(m["authority"], 0) + 1

print("【法規分佈】")
for law, cnt in sorted(laws.items(), key=lambda x: -x[1]):
    print(f"  {cnt} 條  {law}")

print("\n【條文類型分佈】")
type_label = {"penalty": "罰則", "procedure": "程序", "obligation": "義務", "general": "一般"}
for t, cnt in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {cnt} 條  {t:12s} ({type_label.get(t, t)})")

print("\n【效力層級分佈】")
auth_label = {"local": "地方（桃園市）", "central": "中央"}
for a, cnt in sorted(auths.items()):
    print(f"  {cnt} 條  {a:8s} ({auth_label.get(a, a)})")

# ── 2. 每個 Chunk 詳細資訊 ────────────────────────────────────────
print("\n" + "=" * 70)
print("  各 Chunk 完整資訊（含 Metadata）")
print("=" * 70)

for i, chunk in enumerate(chunks):
    meta = chunk["metadata"]
    text = chunk["text"]
    lines = text.split("\n")
    header = lines[0]  # 【法規名稱 條文號】
    content = "\n".join(lines[1:]).strip()

    print(f"\n┌─ Chunk #{i:02d}  (ChromaDB ID: law_{i:04d}) {'─' * 30}")
    print(f"│  法規名稱    │ {meta['law_name']}")
    print(f"│  條文編號    │ {meta['article_num']}")
    print(f"│  條文類型    │ {meta['article_type']:12s} → {type_label.get(meta['article_type'], '')}")
    print(f"│  效力層級    │ {meta['authority']:8s} → {auth_label.get(meta['authority'], '')}")
    print(f"│  來源檔案    │ {meta['source_file']}")
    print(f"│  引用索引鍵  │ {meta['citation_key']}")
    print(f"│  文字長度    │ {len(text)} 字元")
    print(f"│  ChromaDB 標頭 → {header}")
    print(f"├─ 條文內容 {'─' * 50}")
    for line in content.split("\n"):
        if line.strip():
            # 每行最多印 65 字元，超過折行
            while len(line) > 65:
                print(f"│  {line[:65]}")
                line = "   " + line[65:]
            print(f"│  {line}")
    print(f"└{'─' * 68}")

# ── 3. ChromaDB 實際儲存狀態 ──────────────────────────────────────
print("\n" + "=" * 70)
print("  ChromaDB 向量資料庫狀態")
print("=" * 70)

try:
    collection = _get_collection()
    count = collection.count()
    print(f"\n  Collection 名稱 : tuflow_laws")
    print(f"  已存入 chunks   : {count} 條")
    print(f"  向量資料庫路徑  : {settings.chroma_db_path}")

    if count > 0:
        # 取出所有 metadata（不含向量）
        all_data = collection.get(include=["metadatas", "documents"])
        ids = all_data["ids"]
        metas = all_data["metadatas"]
        docs = all_data["documents"]

        print(f"\n  已存入的 IDs：{ids}")
        print(f"\n  各條文的向量維度：768 (paraphrase-multilingual-mpnet-base-v2)")
        print(f"\n  Metadata 欄位清單：{list(metas[0].keys()) if metas else '—'}")

        print(f"\n  法規問答語意相似度範例（模擬查詢）：")
        print(f"  ─────────────────────────────────────")
        print(f"  當使用者問「棄土罰則」，ChromaDB 會依餘弦相似度排序，")
        print(f"  返回最相關的 Top-5 條文，再由 Groq LLM 組裝回答。")
    else:
        print("\n  ⚠ ChromaDB 目前為空，請執行：")
        print("     python -m backend.scripts.ingest_laws")
except Exception as e:
    print(f"\n  ⚠ ChromaDB 連線失敗：{e}")
    print("  （解析結果已顯示於上方，ChromaDB 需後端環境啟動）")
