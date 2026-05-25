"""
智慧媒合 API 路由
/api/match/*
"""
import uuid
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.database import get_connection
from backend.models.site import SiteCreate, SiteResponse
from backend.models.match import (
    MatchRequest, MatchResponse, MatchRecord, MatchStatusUpdate
)
from backend.services.match_service import run_matching, save_match_record

router = APIRouter(prefix="/api/match", tags=["智慧媒合"])


# ── 新增工地 ──────────────────────────────────────────────────────
@router.post("/sites", summary="新增工地（供方/需方/土資場）")
def create_site(payload: SiteCreate):
    site_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO sites
            (id, role, name, address, lat, lng, soil_type, soil_code,
             volume_m3, price_per_m3, available_from, available_until)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            site_id, payload.role, payload.name, payload.address,
            payload.lat, payload.lng, payload.soil_type, payload.soil_code,
            payload.volume_m3, payload.price_per_m3,
            payload.available_from, payload.available_until
        ))
        conn.commit()
    finally:
        conn.close()
    return {"site_id": site_id, "created": True}


# ── 查詢工地清單 ───────────────────────────────────────────────────
@router.get("/sites", summary="查詢工地清單")
def list_sites(
    role: Optional[str] = Query(default=None, description="supply|demand|dump"),
    soil_type: Optional[str] = Query(default=None),
):
    conn = get_connection()
    query = "SELECT * FROM sites WHERE 1=1"
    params = []
    if role:
        query += " AND role = ?"
        params.append(role)
    if soil_type:
        query += " AND soil_type = ?"
        params.append(soil_type)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    sites = [dict(row) for row in rows]
    return {"sites": sites, "total": len(sites)}


# ── 執行 AI 媒合 ───────────────────────────────────────────────────
@router.post("/run", summary="對供方工地執行 AI 媒合")
def run_match(payload: MatchRequest):
    max_dist = 50.0
    if payload.filters and payload.filters.max_distance_km:
        max_dist = payload.filters.max_distance_km

    try:
        result = run_matching(
            supply_id=payload.supply_id,
            max_results=payload.max_results,
            max_distance_km=max_dist,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return result


# ── 更新媒合狀態 ───────────────────────────────────────────────────
@router.patch("/matches/{match_id}", summary="更新媒合狀態")
def update_match_status(match_id: str, payload: MatchStatusUpdate):
    conn = get_connection()
    row = conn.execute("SELECT id FROM matches WHERE id = ?", (match_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="媒合記錄不存在")
    conn.execute("UPDATE matches SET status = ? WHERE id = ?", (payload.status, match_id))
    conn.commit()
    conn.close()
    return {"match_id": match_id, "status": payload.status, "updated": True}


# ── 取得媒合記錄清單 ───────────────────────────────────────────────
@router.get("/matches", summary="取得所有媒合記錄")
def list_matches():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM matches ORDER BY matched_at DESC").fetchall()
    conn.close()
    return {"matches": [dict(row) for row in rows]}


# ── Demo 資料端點 ──────────────────────────────────────────────────
@router.get("/demo", summary="取得 Demo 工地與媒合資料")
def get_demo_data():
    """載入 data/demo/*.json 的展示資料供前端使用"""
    import json
    import os
    from backend.config import get_settings
    settings = get_settings()

    demo_path = settings.demo_data_path
    result = {}

    for filename in ["sites.json", "matches.json"]:
        filepath = os.path.join(demo_path, filename)
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as f:
                key = filename.replace(".json", "")
                result[key] = json.load(f)

    return result
