"""
自動填單服務
1. extract_fields() — 呼叫 Groq LLM 提取 B 類欄位
2. create_manifest() — 建立聯單並寫入 SQLite
3. export_pdf()     — 產生 PDF（WeasyPrint）
"""
import uuid
import json
import re
from datetime import datetime
from typing import Optional

from backend.database import get_connection
from backend.llm.wrapper import chat_json
from backend.llm.prompts import FORM_EXTRACT_SYSTEM, form_extract_user
from backend.models.form import ExtractedFields, SystemFields, ExtractResponse


# ─── 欄位提取 ────────────────────────────────────────────────────
def extract_fields(
    raw_text:      str,
    system_fields: Optional[SystemFields] = None,
) -> ExtractResponse:
    """
    使用 Groq LLM 從自然語言提取 B 類電子聯單欄位

    後端離線或 API 金鑰未設定時，自動 fallback 到正則解析
    """
    route_list = system_fields.route_list if system_fields else []

    try:
        user_msg = form_extract_user(raw_text, route_list)
        result   = chat_json(FORM_EXTRACT_SYSTEM, user_msg)

        # 取出信心度
        confidence = result.pop("confidence", {})

        # 驗證並建立 ExtractedFields
        extracted = ExtractedFields(
            route_name       = result.get("route_name"),
            actual_volume_m3 = _safe_float(result.get("actual_volume_m3")),
            driver_name      = result.get("driver_name"),
            driver_id        = _validate_id(result.get("driver_id")),
            truck_head_plate = _validate_plate(result.get("truck_head_plate")),
            truck_body_plate = _validate_plate(result.get("truck_body_plate")),
            confidence       = confidence,
        )

    except Exception:
        # Fallback：正則解析
        extracted, confidence = _regex_parse(raw_text)

    # 計算缺少的必要欄位
    required_keys = ["route_name", "actual_volume_m3", "driver_name", "driver_id",
                     "truck_head_plate", "truck_body_plate"]
    missing = [k for k in required_keys if not getattr(extracted, k)]

    return ExtractResponse(
        extracted=extracted,
        confidence=confidence,
        missing_fields=missing,
    )


def _safe_float(val) -> Optional[float]:
    try:
        v = float(val)
        return v if 0.1 <= v <= 30.0 else None
    except (TypeError, ValueError):
        return None


def _validate_id(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    val = val.strip().upper()
    return val if re.match(r"^[A-Z][12]\d{8}$", val) else None


def _validate_plate(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    val = val.strip().upper()
    # 標準化格式：確保有連字號
    val = re.sub(r"([A-Z]{2,3})\s*-?\s*(\d{4})", r"\1-\2", val)
    return val if re.match(r"^[A-Z]{2,3}-\d{4}$", val) else None


def _regex_parse(text: str) -> tuple[ExtractedFields, dict]:
    """後端離線時的簡易正則解析（fallback）"""
    result = {}
    confidence = {}

    # 路線
    m = re.search(r"(路線[一二三四五六七八九十\d]+)", text)
    if m:
        result["route_name"] = m.group(1)
        confidence["route_name"] = 0.7

    # 體積
    m = re.search(r"(\d+\.?\d*)\s*方", text)
    if m:
        v = float(m.group(1))
        result["actual_volume_m3"] = v if 0.1 <= v <= 30.0 else None
        confidence["actual_volume_m3"] = 0.8

    # 身份證
    m = re.search(r"[A-Z][12]\d{8}", text, re.IGNORECASE)
    if m:
        result["driver_id"] = m.group().upper()
        confidence["driver_id"] = 0.95

    # 車號
    plates = re.findall(r"[A-Z]{2,3}-?\d{4}", text, re.IGNORECASE)
    plates = [p.upper().replace(" ", "").replace("—", "-") for p in plates]
    if len(plates) >= 1:
        result["truck_head_plate"] = _validate_plate(plates[0])
        confidence["truck_head_plate"] = 0.9
    if len(plates) >= 2:
        result["truck_body_plate"] = _validate_plate(plates[1])
        confidence["truck_body_plate"] = 0.9

    # 姓名（在身份證前的中文）
    m = re.search(r"([^\s，,、A-Z0-9]{2,4})\s*[，,]?\s*[A-Z][12]\d{8}", text)
    if m:
        result["driver_name"] = m.group(1)
        confidence["driver_name"] = 0.75

    extracted = ExtractedFields(**{k: v for k, v in result.items() if v is not None},
                                confidence=confidence)
    return extracted, confidence


# ─── 建立聯單 ────────────────────────────────────────────────────
def create_manifest(
    system_fields:   SystemFields,
    extracted_fields: ExtractedFields,
    match_id:        Optional[str] = None,
) -> dict:
    """建立電子聯單，寫入 SQLite，回傳聯單資訊"""
    manifest_id = f"TY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

    # 產生聯單序號：出土流編 + 收土流編 + 土質 + 8位流水號
    conn = get_connection()
    seq_row = conn.execute(
        "SELECT COUNT(*) as cnt FROM manifests WHERE project_code = ?",
        (system_fields.project_code,)
    ).fetchone()
    seq_num = (seq_row["cnt"] + 1) if seq_row else 1
    manifest_number = (
        f"{system_fields.project_code or 'XXXX'}"
        f"-{system_fields.disposal_site_code or 'YYYY'}"
        f"-{system_fields.soil_code or 'B1'}"
        f"-{seq_num:08d}"
    )

    route_list_json = json.dumps(system_fields.route_list, ensure_ascii=False)
    now = datetime.now().isoformat()

    conn.execute("""
        INSERT INTO manifests
        (id, manifest_number, project_name, project_code, disposal_site_code,
         disposal_site_name, soil_code, total_volume_m3, route_list, manifest_status,
         route_name, actual_volume_m3, driver_name, driver_id,
         truck_head_plate, truck_body_plate,
         raw_input, match_id, status, created_at)
        VALUES (?,?,?,?,?, ?,?,?,?,?, ?,?,?,?, ?,?, ?,?,?,?)
    """, (
        manifest_id, manifest_number,
        system_fields.project_name, system_fields.project_code,
        system_fields.disposal_site_code, system_fields.disposal_site_name,
        system_fields.soil_code, system_fields.total_volume_m3,
        route_list_json, system_fields.manifest_status,
        extracted_fields.route_name, extracted_fields.actual_volume_m3,
        extracted_fields.driver_name, extracted_fields.driver_id,
        extracted_fields.truck_head_plate, extracted_fields.truck_body_plate,
        None, match_id, "submitted", now
    ))
    conn.commit()
    conn.close()

    return {
        "manifest_id":     manifest_id,
        "manifest_number": manifest_number,
        "manifest_status": 1,
        "status":          "submitted",
    }


# ─── PDF 匯出 ────────────────────────────────────────────────────
def export_manifest_pdf(manifest_id: str) -> bytes:
    """
    匯出電子聯單 PDF（使用 reportlab，無需 GTK 系統依賴）
    支援繁體中文（含內建字體）
    """
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    conn = get_connection()
    row = conn.execute("SELECT * FROM manifests WHERE id = ?", (manifest_id,)).fetchone()
    conn.close()

    if not row:
        raise ValueError(f"聯單不存在：{manifest_id}")

    mf = dict(row)

    # 注冊 CID 字體（支援繁體中文）
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    zh_style = ParagraphStyle(
        'zh', fontName='STSong-Light', fontSize=10,
        leading=16, parent=styles['Normal']
    )
    title_style = ParagraphStyle(
        'title', fontName='STSong-Light', fontSize=16,
        alignment=1, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'sub', fontName='STSong-Light', fontSize=9,
        alignment=1, textColor=colors.grey
    )

    def row_data(label, value):
        return [
            Paragraph(label, zh_style),
            Paragraph(str(value) if value else '—', zh_style)
        ]

    def section_header(text):
        return [
            Paragraph(text, ParagraphStyle(
                'sec', fontName='STSong-Light', fontSize=11,
                textColor=colors.white, alignment=1
            )),
            ''
        ]

    story = [
        Paragraph('營建剩餘土石方電子聯單', title_style),
        Paragraph('桃園市 TuFlow 土不落 AI 智慧土方循環管理系統', sub_style),
        Paragraph(f'聯單序號：{mf.get("manifest_number", "—")}', sub_style),
        Spacer(1, 0.4*cm),
    ]

    # 表格資料
    data = [
        section_header('A 類 — 系統欄位'),
        row_data('工程名稱',     mf.get('project_name')),
        row_data('出土流向編號', mf.get('project_code')),
        row_data('收容場所代碼', mf.get('disposal_site_code')),
        row_data('收容場所名稱', mf.get('disposal_site_name')),
        row_data('土質代碼',     mf.get('soil_code')),
        row_data('申報土方量',   f'{mf.get("total_volume_m3","—")} m³'),
        section_header('B 類 — 運載資訊'),
        row_data('出場路線',     mf.get('route_name')),
        row_data('實際出土量',   f'{mf.get("actual_volume_m3","—")} m³' if mf.get('actual_volume_m3') else '—'),
        row_data('駕駛人姓名',   mf.get('driver_name')),
        row_data('駕駛人身份證', mf.get('driver_id')),
        row_data('車頭車號',     mf.get('truck_head_plate')),
        row_data('車斗車號',     mf.get('truck_body_plate')),
    ]

    col_widths = [5*cm, 12*cm]
    tbl = Table(data, colWidths=col_widths, repeatRows=0)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0),  (-1, 0),  colors.HexColor('#2d6a4f')),  # section A
        ('BACKGROUND', (0, 7),  (-1, 7),  colors.HexColor('#2d6a4f')),  # section B
        ('TEXTCOLOR',  (0, 0),  (-1, 0),  colors.white),
        ('TEXTCOLOR',  (0, 7),  (-1, 7),  colors.white),
        ('SPAN',       (0, 0),  (-1, 0)),
        ('SPAN',       (0, 7),  (-1, 7)),
        ('BACKGROUND', (0, 1),  (0, -1),  colors.HexColor('#f5f5f5')),
        ('GRID',       (0, 0),  (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN',     (0, 0),  (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0),  (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    story.append(tbl)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        f'列印時間：{datetime.now().strftime("%Y-%m-%d %H:%M")} · 本聯單由 TuFlow 自動產生',
        ParagraphStyle('footer', fontName='STSong-Light', fontSize=8,
                       textColor=colors.grey, alignment=1)
    ))

    doc.build(story)
    return buf.getvalue()
