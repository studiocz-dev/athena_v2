# Quick Backtest Runner for Athena Bot
# Tests trading strategies against historical data

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Athena Bot - Backtesting" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if tabulate is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$tabulateCheck = python -c "import tabulate; print('OK')" 2>&1
if ($tabulateCheck -ne "OK") {
    Write-Host "Installing tabulate..." -ForegroundColor Yellow
    pip install tabulate
}

Write-Host ""
Write-Host "Starting backtest..." -ForegroundColor Green
Write-Host ""

# Run backtest
python backtest.py

Write-Host ""
Write-Host "Backtest complete!" -ForegroundColor Green
Write-Host ""
