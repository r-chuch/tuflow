"""
Demo 資料匯入腳本
從 data/demo/*.json 讀取假資料並寫入 SQLite

執行方式（.venv 啟動後）：
    python -m backend.scripts.seed_demo_data
"""
import json
import os
import sys

# 確保根目錄在 PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.database import init_db, get_connection
from backend.config import get_settings

settings = get_settings()
DEMO_PATH = settings.demo_data_path


def load_json(filename: str) -> list:
    filepath = os.path.join(DEMO_PATH, filename)
    if not os.path.exists(filepath):
        print(f"⚠️  找不到：{filepath}")
        return []
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def seed_sites(conn) -> int:
    sites = load_json("sites.json")
    count = 0
    for s in sites:
        existing = conn.execute("SELECT id FROM sites WHERE id = ?", (s["id"],)).fetchone()
        if existing:
            continue
        conn.execute("""
            INSERT INTO sites
            (id, role, name, address, lat, lng, soil_type, soil_code,
             volume_m3, price_per_m3, available_from, available_until, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            s["id"], s["role"], s["name"], s.get("address"),
            s["lat"], s["lng"], s["soil_type"], s.get("soil_code"),
            s["volume_m3"], s.get("price_per_m3"),
            s.get("available_from"), s.get("available_until"),
            s.get("status", "active")
        ))
        count += 1
    return count


def seed_matches(conn) -> int:
    matches = load_json("matches.json")
    count = 0
    for m in matches:
        existing = conn.execute("SELECT id FROM matches WHERE id = ?", (m["id"],)).fetchone()
        if existing:
            continue
        conn.execute("""
            INSERT INTO matches
            (id, supply_site_id, demand_site_id, supply_name, demand_name,
             supply_address, demand_address, supply_lat, supply_lng, demand_lat, demand_lng,
             volume_matched, distance_km, score_total, score_distance, score_quantity, score_compat,
             soil_type_supply, soil_type_demand, soil_code, status, matched_at)
            VALUES (?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?)
        """, (
            m["id"], m["supply_site_id"], m["demand_site_id"],
            m.get("supply_name"), m.get("demand_name"),
            m.get("supply_address"), m.get("demand_address"),
            m.get("supply_lat"), m.get("supply_lng"),
            m.get("demand_lat"), m.get("demand_lng"),
            m["volume_matched"], m.get("distance_km"),
            m.get("score_total"), m.get("score_distance"),
            m.get("score_quantity"), m.get("score_compat"),
            m.get("soil_type_supply"), m.get("soil_type_demand"),
            m.get("soil_code"), m.get("status", "proposed"),
            m.get("matched_at")
        ))
        count += 1
    return count


def seed_manifests(conn) -> int:
    manifests = load_json("manifests.json")
    count = 0
    for mf in manifests:
        existing = conn.execute("SELECT id FROM manifests WHERE id = ?", (mf["id"],)).fetchone()
        if existing:
            continue
        # route_list 序列化為 JSON 字串
        route_list = json.dumps(mf.get("route_list", []), ensure_ascii=False)
        conn.execute("""
            INSERT INTO manifests
            (id, manifest_number, project_name, project_code, disposal_site_code,
             disposal_site_name, soil_code, total_volume_m3, route_list, manifest_status,
             route_name, actual_volume_m3, driver_name, driver_id,
             truck_head_plate, truck_body_plate, photo_head, photo_top, photo_content,
             raw_input, match_id, status, created_at, submitted_at)
            VALUES (?,?,?,?,?, ?,?,?,?,?, ?,?,?,?, ?,?,?,?,?, ?,?,?,?,?)
        """, (
            mf["id"], mf.get("manifest_number"), mf.get("project_name"),
            mf.get("project_code"), mf.get("disposal_site_code"),
            mf.get("disposal_site_name"), mf.get("soil_code"),
            mf.get("total_volume_m3"), route_list,
            mf.get("manifest_status", 0),
            mf.get("route_name"), mf.get("actual_volume_m3"),
            mf.get("driver_name"), mf.get("driver_id"),
            mf.get("truck_head_plate"), mf.get("truck_body_plate"),
            mf.get("photo_head"), mf.get("photo_top"), mf.get("photo_content"),
            mf.get("raw_input"), mf.get("match_id"),
            mf.get("status", "draft"),
            mf.get("created_at"), mf.get("submitted_at")
        ))
        count += 1
    return count


def main():
    print("[*] Loading demo data...")
    init_db()

    conn = get_connection()
    try:
        sites_n    = seed_sites(conn)
        matches_n  = seed_matches(conn)
        manifests_n = seed_manifests(conn)
        conn.commit()
    finally:
        conn.close()

    print(f"[OK] Sites:     {sites_n}")
    print(f"[OK] Matches:   {matches_n}")
    print(f"[OK] Manifests: {manifests_n}")
    print("[DONE] Demo data imported")


if __name__ == "__main__":
    main()
