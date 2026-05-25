"""
自動填單 API 路由
/api/form/*
"""
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.database import get_connection
from backend.models.form import (
    ExtractRequest, ExtractResponse,
    ManifestCreate, ManifestResponse,
)
from backend.services.form_service import (
    extract_fields, create_manifest, export_manifest_pdf
)

router = APIRouter(prefix="/api/form", tags=["電子聯單"])


# ── 提取欄位 ──────────────────────────────────────────────────────
@router.post("/extract", response_model=ExtractResponse, summary="AI 提取 B 類欄位")
def api_extract(payload: ExtractRequest):
    return extract_fields(payload.raw_text, payload.system_fields)


# ── 建立聯單 ──────────────────────────────────────────────────────
@router.post("/create", response_model=ManifestResponse, summary="建立電子聯單")
def api_create(payload: ManifestCreate):
    try:
        return create_manifest(
            payload.system_fields,
            payload.extracted_fields,
            payload.match_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── 更新聯單 ──────────────────────────────────────────────────────
@router.patch("/manifests/{manifest_id}", summary="更新聯單欄位")
def api_update(manifest_id: str, payload: dict):
    conn = get_connection()
    row = conn.execute("SELECT id FROM manifests WHERE id = ?", (manifest_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="聯單不存在")

    # 只允許更新 B 類欄位
    allowed = {"route_name", "actual_volume_m3", "driver_name", "driver_id",
               "truck_head_plate", "truck_body_plate"}
    updates = {k: v for k, v in payload.items() if k in allowed}

    if updates:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"UPDATE manifests SET {set_clause} WHERE id = ?",
            list(updates.values()) + [manifest_id]
        )
        conn.commit()
    conn.close()
    return {"manifest_id": manifest_id, "updated": True}


# ── 取得聯單詳情 ──────────────────────────────────────────────────
@router.get("/manifests/{manifest_id}", summary="取得聯單詳情")
def api_get_manifest(manifest_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM manifests WHERE id = ?", (manifest_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="聯單不存在")
    mf = dict(row)
    # route_list JSON 解析
    if mf.get("route_list"):
        try:
            mf["route_list"] = json.loads(mf["route_list"])
        except Exception:
            mf["route_list"] = []
    return mf


# ── 匯出 PDF ──────────────────────────────────────────────────────
@router.get("/manifests/{manifest_id}/export-pdf", summary="匯出 PDF")
def api_export_pdf(manifest_id: str):
    try:
        pdf_bytes = export_manifest_pdf(manifest_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="tuflow_{manifest_id}.pdf"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 生成失敗：{e}")


# ── Demo 資料 ────────────────────────────────────────────────────
@router.get("/demo", summary="取得 Demo 聯單資料")
def api_demo():
    import os
    from backend.config import get_settings
    settings = get_settings()
    filepath = os.path.join(settings.demo_data_path, "manifests.json")
    if not os.path.exists(filepath):
        return {"manifests": []}
    with open(filepath, encoding="utf-8") as f:
        return {"manifests": json.load(f)}
