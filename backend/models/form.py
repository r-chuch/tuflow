"""
電子聯單資料模型
A 類：系統唯讀欄位
B 類：NLP 提取目標欄位
依政府 form_instruction.md 規格設計
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict


class SystemFields(BaseModel):
    """A 類：系統帶入欄位（唯讀，前端不可修改）"""
    project_name:        Optional[str] = None      # 工程名稱
    project_code:        Optional[str] = None      # 出土流向編號
    disposal_site_code:  Optional[str] = None      # 收容處理場所流向編號
    disposal_site_name:  Optional[str] = None      # 收容處理場所名稱
    soil_code:           Optional[str] = Field(default=None, pattern=r"^B[1-7]$")  # B1~B7
    total_volume_m3:     Optional[float] = Field(default=None, ge=0)
    route_list:          list[str] = []            # 可選路線清單
    manifest_status:     int = Field(default=0, ge=0, le=9)  # 聯單狀態


class ExtractedFields(BaseModel):
    """B 類：NLP 提取目標欄位（由語音/文字輸入後 LLM 填入）"""
    route_name:          Optional[str] = None
    actual_volume_m3:    Optional[float] = Field(
        default=None, ge=0.1, le=30.0,
        description="實際出土量（單車）上限 30 m³"
    )
    driver_name:         Optional[str] = Field(default=None, min_length=2, max_length=20)
    driver_id:           Optional[str] = Field(
        default=None,
        pattern=r"^[A-Z][12]\d{8}$",
        description="台灣身份證，如 A123456789"
    )
    truck_head_plate:    Optional[str] = Field(
        default=None,
        pattern=r"^[A-Z]{2,3}-\d{4}$",
        description="車頭車號，如 KAA-1234"
    )
    truck_body_plate:    Optional[str] = Field(
        default=None,
        pattern=r"^[A-Z]{2,3}-\d{4}$",
        description="車斗車號"
    )
    photo_head:          Optional[str] = None      # 出場車頭照片路徑
    photo_top:           Optional[str] = None      # 出場車頂照片路徑
    photo_content:       Optional[str] = None      # 進場內容照片路徑
    confidence:          Dict[str, float] = {}


class ExtractRequest(BaseModel):
    raw_text:      str = Field(min_length=1, max_length=2000)
    source:        Literal["text", "voice_transcript"] = "text"
    system_fields: Optional[SystemFields] = None


class ExtractResponse(BaseModel):
    extracted:      ExtractedFields
    confidence:     Dict[str, float]
    missing_fields: list[str]


class ManifestCreate(BaseModel):
    system_fields:   SystemFields
    extracted_fields: ExtractedFields
    match_id:        Optional[str] = None


class ManifestResponse(BaseModel):
    manifest_id:     str
    manifest_number: Optional[str]
    manifest_status: int
    status:          str
