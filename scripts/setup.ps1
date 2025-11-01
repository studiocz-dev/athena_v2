# Setup Script for Athena Trading Bot
# Run this script to perform initial setup

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Athena Trading Bot - Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/6] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

if ($pythonVersion -match "Python 3\.([0-9]+)") {
    $minorVersion = [int]$matches[1]
    if ($minorVersion -lt 9) {
        Write-Host "ERROR: Python 3.9 or higher required!" -ForegroundColor Red
        exit 1
    }
}

# Create virtual environment
Write-Host ""
Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/6] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[4/6] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "Dependencies installed" -ForegroundColor Green

# Create directories
Write-Host ""
Write-Host "[5/6] Creating directories..." -ForegroundColor Yellow
$directories = @("logs", "trading_data")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "Already exists: $dir" -ForegroundColor Green
    }
}

# Setup .env file
Write-Host ""
Write-Host "[6/6] Setting up environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env file already exists" -ForegroundColor Yellow
    $response = Read-Host "Overwrite? (y/N)"
    if ($response -ne "y") {
        Write-Host "Keeping existing .env file" -ForegroundColor Green
    } else {
        Copy-Item ".env.example" ".env" -Force
        Write-Host "Created new .env file" -ForegroundColor Green
    }
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file from template" -ForegroundColor Green
}

# Final instructions
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete! ✓" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your API keys" -ForegroundColor White
Write-Host "   - Discord Bot Token" -ForegroundColor White
Write-Host "   - Binance API Key & Secret" -ForegroundColor White
Write-Host ""
Write-Host "2. Start the bot:" -ForegroundColor White
Write-Host "   python bot.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. For detailed instructions, see:" -ForegroundColor White
Write-Host "   - README.md" -ForegroundColor Cyan
Write-Host "   - QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Need help? Read the documentation!" -ForegroundColor Yellow
Write-Host ""
