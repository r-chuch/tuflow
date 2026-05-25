"""測試媒合功能對 Demo 資料的計算"""
from backend.services.match_service import run_matching

# 測試 site-001（桃園中山路新建大樓工程）
result = run_matching("site-001", max_results=5, max_distance_km=50.0)
print(f"Supply: {result.supply_name}")
print(f"Found: {result.total_found} matches")
print()
for i, m in enumerate(result.matches):
    print(f"  #{i+1} {m.name}")
    print(f"      Distance: {m.distance_km} km | Score: {m.score}")
    print(f"      Breakdown: dist={m.score_breakdown.distance} qty={m.score_breakdown.quantity} compat={m.score_breakdown.compat}")
