# TuFlow 後端啟動腳本
# 使用方式：在專案根目錄執行 .\start_backend.ps1

Set-Location $PSScriptRoot

# 確認 .env 存在
if (-not (Test-Path ".env")) {
    Write-Host "[WARN] .env not found. Copying from .env.example..."
    Copy-Item ".env.example" ".env"
    Write-Host "[INFO] Please edit .env and set GROQ_API_KEY"
}

# 啟動虛擬環境
if (Test-Path ".venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "[ERROR] .venv not found. Run: python -m venv .venv && pip install -r requirements.txt"
    exit 1
}

# 確認資料庫已初始化
$env:PYTHONIOENCODING = "utf-8"
python -c "from backend.database import init_db; init_db()" 2>$null

Write-Host "[OK] Starting TuFlow backend on http://localhost:8001"
Write-Host "[OK] API docs: http://localhost:8001/docs"
Write-Host ""

uvicorn backend.main:app --reload --port 8001
