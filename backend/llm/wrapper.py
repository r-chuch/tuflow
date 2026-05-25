"""
Groq LLM 統一介面
使用 Groq SDK，支援 JSON mode
GROQ_API_KEY 從 .env 讀取，不硬編碼
"""
import json
from groq import Groq
from backend.config import get_settings

settings = get_settings()

# 建立 Groq 客戶端（每次呼叫從 settings 讀取，確保 .env 更新後生效）
def _get_client() -> Groq:
    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY 未設定。\n"
            "請在 .env 檔案中加入：GROQ_API_KEY=gsk_your_key_here\n"
            "至 https://console.groq.com 申請免費金鑰"
        )
    return Groq(api_key=settings.groq_api_key)


def chat_json(
    system_prompt: str,
    user_message:  str,
    model:         str | None = None,
    temperature:   float = 0.1,
    max_tokens:    int   = 2048,
) -> dict:
    """
    呼叫 Groq LLM，強制回傳 JSON 格式。

    Args:
        system_prompt: 系統提示詞
        user_message:  使用者訊息
        model:         模型名稱（預設從 settings 讀取）
        temperature:   溫度（0.1 = 保守穩定）
        max_tokens:    最大輸出 tokens

    Returns:
        dict: 解析後的 JSON 回應

    Raises:
        ValueError: API 金鑰未設定
        json.JSONDecodeError: LLM 回傳非 JSON
    """
    client = _get_client()
    model = model or settings.groq_model

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


def chat_text(
    system_prompt: str,
    user_message:  str,
    model:         str | None = None,
    temperature:   float = 0.7,
    max_tokens:    int   = 1024,
) -> str:
    """
    呼叫 Groq LLM，回傳純文字（非 JSON mode）。
    """
    client = _get_client()
    model = model or settings.groq_model

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
