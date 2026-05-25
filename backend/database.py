"""
TuFlow SQLite 資料庫初始化模組
建立 4 張資料表：sites, matches, manifests, qa_sessions
"""
import sqlite3
import os
from backend.config import get_settings

settings = get_settings()


def get_db_path() -> str:
    """取得資料庫絕對路徑，並確保目錄存在"""
    db_path = settings.db_path
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    return db_path


def get_connection() -> sqlite3.Connection:
    """取得 SQLite 連線（row_factory 設為 dict-like）"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """建立所有資料表（若不存在）"""
    conn = get_connection()
    cursor = conn.cursor()

    # ─── 工地資料（供方 / 需方 / 土資場）───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sites (
            id              TEXT PRIMARY KEY,
            role            TEXT NOT NULL CHECK(role IN ('supply','demand','dump')),
            name            TEXT NOT NULL,
            address         TEXT,
            lat             REAL NOT NULL,
            lng             REAL NOT NULL,
            soil_type       TEXT NOT NULL,   -- class1 | class2 | class3
            soil_code       TEXT,            -- B1~B7（政府代碼）
            volume_m3       REAL NOT NULL,
            price_per_m3    REAL,
            available_from  TEXT,            -- ISO date string
            available_until TEXT,
            status          TEXT DEFAULT 'active',
            created_at      TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # ─── 媒合記錄 ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id                TEXT PRIMARY KEY,
            supply_site_id    TEXT NOT NULL REFERENCES sites(id),
            demand_site_id    TEXT NOT NULL REFERENCES sites(id),
            supply_name       TEXT,
            demand_name       TEXT,
            supply_address    TEXT,
            demand_address    TEXT,
            supply_lat        REAL,
            supply_lng        REAL,
            demand_lat        REAL,
            demand_lng        REAL,
            volume_matched    REAL NOT NULL,
            distance_km       REAL,
            score_total       REAL,
            score_distance    REAL,
            score_quantity    REAL,
            score_compat      REAL,
            soil_type_supply  TEXT,
            soil_type_demand  TEXT,
            soil_code         TEXT,
            status            TEXT DEFAULT 'proposed',
            matched_at        TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # ─── 電子聯單（依政府 form_instruction.md 規格）───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manifests (
            id                  TEXT PRIMARY KEY,        -- TY-XXXXXXXX
            -- A 類：系統唯讀欄位
            manifest_number     TEXT UNIQUE,             -- 聯單序號
            project_name        TEXT,                    -- 工程名稱
            project_code        TEXT,                    -- 出土流編
            disposal_site_code  TEXT,                    -- 收土流編
            disposal_site_name  TEXT,                    -- 收容處理場所名稱
            soil_code           TEXT,                    -- 土質代碼 B1~B7
            total_volume_m3     REAL,                    -- 土方量（m³）
            route_list          TEXT,                    -- JSON 陣列，可選路線
            manifest_status     INTEGER DEFAULT 0,       -- 0~9 狀態機
            -- B 類：NLP 提取目標
            route_name          TEXT,                    -- 出場路線
            actual_volume_m3    REAL,                    -- 實際出土量
            driver_name         TEXT,                    -- 駕駛人姓名
            driver_id           TEXT,                    -- 駕駛人身份證（10碼）
            truck_head_plate    TEXT,                    -- 車頭車號
            truck_body_plate    TEXT,                    -- 車斗車號
            photo_head          TEXT,                    -- 出場車頭照片（路徑）
            photo_top           TEXT,                    -- 出場車頂照片
            photo_content       TEXT,                    -- 進場內容照片
            -- 其他
            raw_input           TEXT,                    -- 原始語音/文字輸入
            match_id            TEXT REFERENCES matches(id),
            status              TEXT DEFAULT 'draft',   -- draft | submitted
            created_at          TEXT DEFAULT (datetime('now','localtime')),
            submitted_at        TEXT
        )
    """)

    # ─── 法規問答記錄 ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qa_sessions (
            id          TEXT PRIMARY KEY,
            question    TEXT NOT NULL,
            answer      TEXT NOT NULL,
            law_refs    TEXT,            -- JSON 陣列字串
            confidence  TEXT DEFAULT 'medium',
            created_at  TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    conn.commit()
    conn.close()
    print("[OK] tuflow.db init done (4 tables)")


if __name__ == "__main__":
    init_db()
