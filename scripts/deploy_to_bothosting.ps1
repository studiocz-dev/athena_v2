# Athena v2 Bot - SFTP Deployment Script
# Upload bot files to bot-hosting.net

# SFTP Connection Details
$SFTPHost = "de1.bot-hosting.net"
$SFTPPort = 2022
$SFTPUser = "1030846920597454929.d0046ffd"
$SFTPPassword = "oEugkjW1NpC64Bf"

# Local paths
$LocalPath = "I:\Discord_Bot\athena_bot"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Athena v2 Bot - SFTP Deployment" -ForegroundColor Cyan
Write-Host "  Target: bot-hosting.net" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if WinSCP is installed
$WinSCPPath = "C:\Program Files (x86)\WinSCP\WinSCP.com"
if (-Not (Test-Path $WinSCPPath)) {
    Write-Host "ERROR: WinSCP not found at: $WinSCPPath" -ForegroundColor Red
    Write-Host "Please install WinSCP from: https://winscp.net/eng/download.php" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Use PSFTP (comes with PuTTY)" -ForegroundColor Yellow
    Write-Host "Download from: https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ WinSCP found" -ForegroundColor Green
Write-Host ""

# Create WinSCP script
$ScriptPath = "$env:TEMP\winscp_upload_script.txt"
$ScriptContent = @"
option batch abort
option confirm off
open sftp://${SFTPUser}:${SFTPPassword}@${SFTPHost}:${SFTPPort}/ -hostkey=*

# Navigate to container directory
cd /home/container

# Upload Python files
lcd "$LocalPath"
put *.py

# Upload configuration files
put requirements.txt
put .env.example
put LICENSE
put README.md

# Upload documentation
put *.md

# Create trading_data directory (empty, for database)
mkdir trading_data 2>/dev/null || echo Directory exists

# Close connection
close
exit
"@

Set-Content -Path $ScriptPath -Value $ScriptContent

Write-Host "Connecting to SFTP server..." -ForegroundColor Yellow
Write-Host "Host: $SFTPHost:$SFTPPort" -ForegroundColor Gray
Write-Host "User: $SFTPUser" -ForegroundColor Gray
Write-Host ""

# Execute WinSCP with the script
& $WinSCPPath /script="$ScriptPath"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  ✓ Deployment Successful!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. SSH into bot-hosting.net" -ForegroundColor White
    Write-Host "2. Navigate to /bot directory" -ForegroundColor White
    Write-Host "3. Create .env file with your API keys" -ForegroundColor White
    Write-Host "4. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "5. Run bot: python auto_trader.py" -ForegroundColor White
    Write-Host ""
    Write-Host "See DEPLOYMENT_BOTHOSTING.md for detailed instructions" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "  ✗ Deployment Failed" -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above." -ForegroundColor Yellow
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- Incorrect credentials" -ForegroundColor White
    Write-Host "- Network/firewall blocking port 2022" -ForegroundColor White
    Write-Host "- Server not accessible" -ForegroundColor White
}

# Clean up temporary script
Remove-Item $ScriptPath -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
