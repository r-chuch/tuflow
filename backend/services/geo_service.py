"""
地理計算服務
使用 geopy geodesic 計算兩點距離（比 Haversine 更精確）
並提供距離評分函數
"""
from geopy.distance import geodesic


def calc_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """計算兩點間的大圓距離（公里）"""
    return round(geodesic((lat1, lng1), (lat2, lng2)).kilometers, 2)


def calc_distance_score(distance_km: float) -> float:
    """
    距離分數（S_distance，0~100）

    ≤ 5  km → 100
    ≤ 10 km → 100 - (d-5)  × 8      [60~100]
    ≤ 20 km → 60  - (d-10) × 4      [20~60]
    ≤ 40 km → 20  - (d-20) × 1      [0~20]
    > 40 km → 0
    """
    d = distance_km
    if d <= 5:
        return 100.0
    elif d <= 10:
        return round(100.0 - (d - 5) * 8, 2)
    elif d <= 20:
        return round(60.0 - (d - 10) * 4, 2)
    elif d <= 40:
        return round(20.0 - (d - 20) * 1, 2)
    else:
        return 0.0
