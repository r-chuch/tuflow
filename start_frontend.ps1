# TuFlow 前端啟動腳本
# 使用方式：在專案根目錄執行 .\start_frontend.ps1

Set-Location "$PSScriptRoot\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "[*] Installing npm packages..."
    npm install
}

Write-Host "[OK] Starting TuFlow frontend on http://localhost:5173"
Write-Host "[OK] Proxy: /api -> http://localhost:8000"
Write-Host ""

npm run dev
