# -*- coding: utf-8 -*-
"""RAG 法規資料快速檢視"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')

from backend.services.rag_service import parse_law_markdown, _get_collection
from backend.config import get_settings

settings = get_settings()
chunks = parse_law_markdown(settings.law_file_path)

TYPE = {'penalty': '罰則', 'procedure': '程序', 'obligation': '義務', 'general': '一般'}
AUTH = {'local': '地方(桃園市)', 'central': '中央'}

print("=" * 75)
print(f"  RAG 法規向量庫資料 — 共 {len(chunks)} 個 Chunks")
print("=" * 75)
print(f"\n{'ID':8} {'條文編號':10} {'類型':16} {'效力':16} 法規名稱")
print("-" * 75)

for i, c in enumerate(chunks):
    m = c['metadata']
    t_zh = TYPE.get(m['article_type'], m['article_type'])
    a_zh = AUTH.get(m['authority'], m['authority'])
    print(f"law_{i:04d}  {m['article_num']:10}  {m['article_type']:10}({t_zh:2})  {m['authority']:8}({a_zh})  {m['law_name']}")

# 詳細 metadata 展示（只印前 3 個作範例）
print("\n" + "=" * 75)
print("  各 Chunk 完整 Metadata 結構（前 3 筆範例）")
print("=" * 75)
for i, c in enumerate(chunks[:3]):
    m = c['metadata']
    t = c['text']
    print(f"\n【Chunk #{i:02d} — law_{i:04d}】")
    print(f"  Metadata 欄位：")
    for k, v in m.items():
        print(f"    {k:15}: {v}")
    preview = t[:120].replace('\n', ' ')
    print(f"  ChromaDB text (前120字): {preview}...")
    print(f"  text 總長度: {len(t)} 字元")

# 統計
print("\n" + "=" * 75)
print("  分類統計")
print("=" * 75)
laws = {}
types = {}
auths = {}
for c in chunks:
    m = c['metadata']
    laws[m['law_name']] = laws.get(m['law_name'], 0) + 1
    types[m['article_type']] = types.get(m['article_type'], 0) + 1
    auths[m['authority']] = auths.get(m['authority'], 0) + 1

print("\n  法規別：")
for law, cnt in sorted(laws.items(), key=lambda x: -x[1]):
    print(f"    {cnt} 條  {law}")

print("\n  條文類型：")
for t, cnt in sorted(types.items(), key=lambda x: -x[1]):
    print(f"    {cnt} 條  {t:12} ({TYPE.get(t, t)})")

print("\n  效力層級：")
for a, cnt in sorted(auths.items()):
    print(f"    {cnt} 條  {a:8} ({AUTH.get(a, a)})")

# ChromaDB 狀態
print("\n" + "=" * 75)
print("  ChromaDB 向量資料庫實際儲存狀態")
print("=" * 75)
try:
    col = _get_collection()
    count = col.count()
    ids = col.get()['ids']
    metas = col.get(include=['metadatas'])['metadatas']
    print(f"\n  Collection  : tuflow_laws")
    print(f"  已存入 docs : {count} 筆")
    print(f"  向量維度    : 768 (paraphrase-multilingual-mpnet-base-v2)")
    print(f"  DB 路徑     : {settings.chroma_db_path}")
    print(f"\n  所有 IDs：")
    for doc_id in ids:
        print(f"    {doc_id}")
    if metas:
        print(f"\n  Metadata 欄位清單（6個）：{list(metas[0].keys())}")
except Exception as e:
    print(f"  ChromaDB 連線失敗: {e}")
