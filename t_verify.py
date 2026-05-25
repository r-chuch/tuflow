"""快速驗證腳本"""
from backend.main import app
from backend.services.match_service import run_matching, calc_total_score
from backend.services.geo_service import calc_distance_km, calc_distance_score

# 測試地理計算
d = calc_distance_km(24.9937, 121.3009, 24.9422, 121.3006)
s = calc_distance_score(d)
score = calc_total_score(800, 1500, 'class1', 'class1', d)

print(f"Distance: {d} km")
print(f"Distance score raw: {s}")
print(f"Total score: {score['total']}")

# 測試 FastAPI app
print(f"FastAPI routes: {len(app.routes)}")
print("All imports OK")
