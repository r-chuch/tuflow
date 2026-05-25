"""
媒合請求與結果模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class MatchFilters(BaseModel):
    max_distance_km: Optional[float] = Field(default=50.0, ge=1.0, le=200.0)


class MatchRequest(BaseModel):
    supply_id: str
    max_results: int = Field(default=5, ge=1, le=20)
    filters: Optional[MatchFilters] = None


class ScoreBreakdown(BaseModel):
    distance: float    # S_distance × 0.40
    quantity: float    # S_quantity × 0.35
    compat: float      # S_compat  × 0.25
    raw_distance: float
    raw_quantity: float
    raw_compat: float


class MatchResultItem(BaseModel):
    site_id: str
    name: str
    address: Optional[str]
    lat: float
    lng: float
    distance_km: float
    score: float
    score_breakdown: ScoreBreakdown
    volume_available: float
    price_per_m3: Optional[float]
    soil_type: str
    soil_code: Optional[str]


class MatchResponse(BaseModel):
    supply_id: str
    supply_name: str
    supply_lat: float
    supply_lng: float
    matches: list[MatchResultItem]
    total_found: int


class MatchRecord(BaseModel):
    id: str
    supply_site_id: str
    demand_site_id: str
    supply_name: Optional[str]
    demand_name: Optional[str]
    supply_address: Optional[str]
    demand_address: Optional[str]
    supply_lat: Optional[float]
    supply_lng: Optional[float]
    demand_lat: Optional[float]
    demand_lng: Optional[float]
    volume_matched: float
    distance_km: Optional[float]
    score_total: Optional[float]
    score_distance: Optional[float]
    score_quantity: Optional[float]
    score_compat: Optional[float]
    soil_type_supply: Optional[str]
    soil_type_demand: Optional[str]
    soil_code: Optional[str]
    status: str
    matched_at: str

    model_config = {"from_attributes": True}


class MatchStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(proposed|confirmed|cancelled)$")
