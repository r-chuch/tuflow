"""
TuFlow 後端設定模組
使用 pydantic-settings 從 .env 讀取環境變數（安全 UI 模式，不硬編碼金鑰）
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # === Groq LLM ===
    groq_api_key: str = Field(default="", description="Groq API 金鑰")
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    groq_model_fast: str = Field(default="llama-3.1-8b-instant")

    # === 資料庫 ===
    database_url: str = Field(default="sqlite:///./data/tuflow.db")
    db_path: str = Field(default="./data/tuflow.db")

    # === ChromaDB ===
    chroma_db_path: str = Field(default="./data/chroma_db")

    # === 法規文件 ===
    law_file_path: str = Field(default="./data/laws/law_tuflow.md")

    # === Demo 資料 ===
    demo_data_path: str = Field(default="./data/demo")

    # === 後端 ===
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000)

    # === CORS ===
    cors_origins: str = Field(default="http://localhost:5173,http://localhost:3000")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """取得快取的設定實例（整個應用共用）

    注意：修改 .env 後必須重啟後端才能生效（lru_cache 在程序存活期間不會重新讀取）
    """
    s = Settings()
    # 啟動時警告：API 金鑰未設定
    if not s.groq_api_key:
        import sys
        print("[WARN] GROQ_API_KEY not set - LLM features disabled (set in .env)", file=sys.stderr)
    return s
