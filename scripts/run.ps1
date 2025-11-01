# Run script for Athena Trading Bot
# This script checks configuration and starts the bot

Write-Host ""
Write-Host "🤖 Starting Athena Trading Bot..." -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create .env file first:" -ForegroundColor Yellow
    Write-Host "1. Copy .env.example to .env" -ForegroundColor White
    Write-Host "2. Edit .env with your API keys" -ForegroundColor White
    Write-Host "3. Run this script again" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✅ Activating virtual environment..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "   Run setup.ps1 first to create it" -ForegroundColor White
}

# Check Python
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python: $pythonCheck" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    exit 1
}

# Check if packages are installed
Write-Host "✅ Checking dependencies..." -ForegroundColor Green
$discordCheck = python -c "import discord; print('OK')" 2>&1
if ($discordCheck -ne "OK") {
    Write-Host "⚠️  Dependencies not installed" -ForegroundColor Yellow
    Write-Host "   Installing now..." -ForegroundColor White
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "🚀 Starting bot..." -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Run the bot
python bot.py
