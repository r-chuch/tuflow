"""
工地資料模型（供方 / 需方 / 土資場）
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date


class SiteCreate(BaseModel):
    role: Literal["supply", "demand", "dump"]
    name: str = Field(min_length=2, max_length=100)
    address: Optional[str] = None
    lat: float = Field(ge=21.0, le=26.5)   # 台灣緯度範圍
    lng: float = Field(ge=119.0, le=122.5)  # 台灣經度範圍
    soil_type: Literal["class1", "class2", "class3"]
    soil_code: Optional[str] = Field(default=None, pattern=r"^B[1-7]$")
    volume_m3: float = Field(gt=0, le=1_000_000)
    price_per_m3: Optional[float] = Field(default=None, ge=0)
    available_from: Optional[str] = None
    available_until: Optional[str] = None


class SiteResponse(BaseModel):
    id: str
    role: str
    name: str
    address: Optional[str]
    lat: float
    lng: float
    soil_type: str
    soil_code: Optional[str]
    volume_m3: float
    price_per_m3: Optional[float]
    available_from: Optional[str]
    available_until: Optional[str]
    status: str
    created_at: str

    model_config = {"from_attributes": True}
