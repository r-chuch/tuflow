"""
智慧媒合服務
評分公式：total = 0.40×S_distance + 0.35×S_quantity + 0.25×S_compat
"""
import uuid
import sqlite3
from typing import Optional

from backend.database import get_connection
from backend.services.geo_service import calc_distance_km, calc_distance_score
from backend.models.match import MatchResultItem, ScoreBreakdown, MatchResponse

# ─── 土質相容矩陣 ───
# 鍵：(供方類型, 需方類型) → 0~100 分
COMPAT_MATRIX: dict[tuple[str, str], float] = {
    ("class1", "class1"): 100.0,
    ("class1", "class2"):  80.0,
    ("class1", "class3"):  40.0,
    ("class2", "class1"):  30.0,
    ("class2", "class2"): 100.0,
    ("class2", "class3"):  60.0,
    ("class3", "class1"):   0.0,
    ("class3", "class2"):  20.0,
    ("class3", "class3"): 100.0,
}

# 權重設定
W_DISTANCE = 0.40
W_QUANTITY = 0.35
W_COMPAT   = 0.25


def calc_quantity_score(supply_vol: float, demand_vol: float) -> float:
    """數量匹配分數（0~100）"""
    if supply_vol <= 0 or demand_vol <= 0:
        return 0.0
    ratio = min(supply_vol, demand_vol) / max(supply_vol, demand_vol)
    return round(ratio * 100, 2)


def calc_compat_score(supply_type: str, demand_type: str) -> float:
    """土質相容分數（0~100）"""
    return COMPAT_MATRIX.get((supply_type, demand_type), 0.0)


def calc_total_score(
    supply_vol: float, demand_vol: float,
    supply_type: str, demand_type: str,
    distance_km: float,
) -> dict:
    """計算完整評分並回傳 breakdown"""
    s_dist = calc_distance_score(distance_km)
    s_qty  = calc_quantity_score(supply_vol, demand_vol)
    s_comp = calc_compat_score(supply_type, demand_type)

    total = round(
        W_DISTANCE * s_dist +
        W_QUANTITY * s_qty +
        W_COMPAT   * s_comp,
        2
    )

    return {
        "total":        total,
        "raw_distance": s_dist,
        "raw_quantity": s_qty,
        "raw_compat":   s_comp,
        "weighted_distance": round(W_DISTANCE * s_dist, 2),
        "weighted_quantity": round(W_QUANTITY * s_qty,  2),
        "weighted_compat":   round(W_COMPAT   * s_comp, 2),
    }


def run_matching(
    supply_id: str,
    max_results: int = 5,
    max_distance_km: float = 50.0,
) -> MatchResponse:
    """
    對指定供方工地執行媒合，返回排序後的需方清單
    """
    conn = get_connection()

    # 取得供方資料
    supply = conn.execute(
        "SELECT * FROM sites WHERE id = ? AND role = 'supply'",
        (supply_id,)
    ).fetchone()

    if not supply:
        conn.close()
        raise ValueError(f"供方工地不存在：{supply_id}")

    # 取得所有 active 需方工地
    demands = conn.execute(
        "SELECT * FROM sites WHERE role = 'demand' AND status = 'active'"
    ).fetchall()

    conn.close()

    results: list[MatchResultItem] = []

    for d in demands:
        dist = calc_distance_km(
            supply["lat"], supply["lng"],
            d["lat"],      d["lng"]
        )

        # 距離過濾
        if dist > max_distance_km:
            continue

        scores = calc_total_score(
            supply_vol=supply["volume_m3"],
            demand_vol=d["volume_m3"],
            supply_type=supply["soil_type"],
            demand_type=d["soil_type"],
            distance_km=dist,
        )

        results.append(MatchResultItem(
            site_id=d["id"],
            name=d["name"],
            address=d["address"],
            lat=d["lat"],
            lng=d["lng"],
            distance_km=dist,
            score=scores["total"],
            score_breakdown=ScoreBreakdown(
                distance=scores["weighted_distance"],
                quantity=scores["weighted_quantity"],
                compat=scores["weighted_compat"],
                raw_distance=scores["raw_distance"],
                raw_quantity=scores["raw_quantity"],
                raw_compat=scores["raw_compat"],
            ),
            volume_available=d["volume_m3"],
            price_per_m3=d["price_per_m3"],
            soil_type=d["soil_type"],
            soil_code=d["soil_code"],
        ))

    # 依總分降序排列，取前 max_results 筆
    results.sort(key=lambda x: x.score, reverse=True)
    results = results[:max_results]

    return MatchResponse(
        supply_id=supply["id"],
        supply_name=supply["name"],
        supply_lat=supply["lat"],
        supply_lng=supply["lng"],
        matches=results,
        total_found=len(results),
    )


def save_match_record(
    supply_id: str,
    demand_id: str,
    volume_matched: float,
    distance_km: float,
    scores: dict,
    supply_soil: str,
    demand_soil: str,
    soil_code: str,
) -> str:
    """將媒合結果存入 matches 資料表，回傳 match id"""
    conn = get_connection()

    supply = conn.execute("SELECT * FROM sites WHERE id = ?", (supply_id,)).fetchone()
    demand = conn.execute("SELECT * FROM sites WHERE id = ?", (demand_id,)).fetchone()

    match_id = str(uuid.uuid4())

    conn.execute("""
        INSERT INTO matches
        (id, supply_site_id, demand_site_id, supply_name, demand_name,
         supply_address, demand_address, supply_lat, supply_lng, demand_lat, demand_lng,
         volume_matched, distance_km, score_total, score_distance, score_quantity, score_compat,
         soil_type_supply, soil_type_demand, soil_code, status)
        VALUES (?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?,?,?, ?,?,?,?)
    """, (
        match_id, supply_id, demand_id,
        supply["name"] if supply else None,
        demand["name"] if demand else None,
        supply["address"] if supply else None,
        demand["address"] if demand else None,
        supply["lat"] if supply else None,
        supply["lng"] if supply else None,
        demand["lat"] if demand else None,
        demand["lng"] if demand else None,
        volume_matched, distance_km,
        scores.get("total"), scores.get("raw_distance"),
        scores.get("raw_quantity"), scores.get("raw_compat"),
        supply_soil, demand_soil, soil_code, "proposed"
    ))

    conn.commit()
    conn.close()
    return match_id
