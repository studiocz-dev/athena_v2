# Deploying Athena v2 to bot-hosting.net

## 📋 Overview

This guide covers deploying your Athena v2 automated trading bot to bot-hosting.net for 24/7 operation.

## 🔐 Server Details

- **Host**: `de1.bot-hosting.net`
- **Port**: `2022` (SFTP)
- **Protocol**: SFTP
- **Username**: `1030846920597454929.d0046ffd`
- **Remote Path**: `/bot` (recommended)

## 🚀 Quick Deployment

### Option 1: Automated Deployment (PowerShell Script)

Run the deployment script from your local machine:

```powershell
.\deploy_to_bothosting.ps1
```

**Prerequisites**:
- WinSCP installed: https://winscp.net/eng/download.php
- Or PuTTY/PSFTP: https://www.chiark.greenend.org.uk/~sgtatham/putty/

The script will:
1. Connect to bot-hosting.net via SFTP
2. Create `/bot` directory structure
3. Upload all Python files, requirements, and documentation
4. Set up `trading_data` directory for database

### Option 2: Manual Deployment via SFTP Client

1. **Connect via SFTP**:
   - Host: `de1.bot-hosting.net:2022`
   - Username: `1030846920597454929.d0046ffd`
   - Password: (from credentials)

2. **Upload files**:
   ```
   /bot/
   ├── *.py (all Python files)
   ├── requirements.txt
   ├── .env (create on server)
   ├── README.md
   ├── LICENSE
   └── docs/
       ├── AUTO_TRADING_GUIDE.md
       ├── MTF_OPTIMIZATION_GUIDE.md
       ├── WIN_RATE_ANALYSIS.md
       └── ...
   ```

3. **Create directories**:
   - `/bot/trading_data/` (for SQLite database)
   - `/bot/docs/` (for documentation)

### Option 3: Deploy from GitHub

SSH into bot-hosting.net and clone the repository:

```bash
ssh 1030846920597454929.d0046ffd@de1.bot-hosting.net -p 2022
cd /
git clone https://github.com/studiocz-dev/athena_v2.git bot
cd bot
```

## ⚙️ Server Setup

### 1. SSH into Server

```bash
ssh 1030846920597454929.d0046ffd@de1.bot-hosting.net -p 2022
```

### 2. Navigate to Bot Directory

```bash
cd /bot
```

### 3. Create Environment File

Create `.env` file with your configuration:

```bash
nano .env
```

**Required contents**:
```env
# Discord Bot Token
DISCORD_TOKEN=your_actual_discord_token_here

# Binance API Keys (use TESTNET for testing)
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret

# Trading Mode (testnet recommended initially)
USE_TESTNET=true

# Discord Channel IDs (already set in code)
# SIGNALS_CHANNEL_ID=1423658108286275717
# REPORTS_CHANNEL_ID=1432616229159571476
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

### 4. Install Dependencies

Check Python version (requires 3.9+):
```bash
python3 --version
```

Install required packages:
```bash
pip3 install -r requirements.txt
```

Or install individually:
```bash
pip3 install discord.py==2.3.2 python-binance==1.0.19 pandas numpy python-dotenv ta tabulate
```

### 5. Test Configuration

Quick test to verify setup:
```bash
python3 test_setup.py
```

This will verify:
- ✓ API keys loaded
- ✓ Binance connection (testnet)
- ✓ Discord token present
- ✓ Dependencies installed

### 6. Run Bot

**Test run** (foreground):
```bash
python3 auto_trader.py
```

Watch for:
- "Connected to Binance Futures TESTNET" ✓
- "Performance database initialized" ✓
- "Bot logged in as FutureBot#6502" ✓
- "Background tasks started" ✓

Press `Ctrl+C` to stop if testing.

### 7. Run as Background Service

**Option A: Using screen** (recommended):
```bash
screen -S athena_bot
python3 auto_trader.py
```

To detach: Press `Ctrl+A`, then `D`

To reattach: `screen -r athena_bot`

To stop: Reattach and press `Ctrl+C`

**Option B: Using nohup**:
```bash
nohup python3 auto_trader.py > bot.log 2>&1 &
```

Check logs: `tail -f bot.log`

Stop: `ps aux | grep auto_trader.py` then `kill <PID>`

**Option C: Using systemd** (if available):

Create service file `/etc/systemd/system/athena-bot.service`:
```ini
[Unit]
Description=Athena v2 Automated Trading Bot
After=network.target

[Service]
Type=simple
User=1030846920597454929.d0046ffd
WorkingDirectory=/bot
ExecStart=/usr/bin/python3 /bot/auto_trader.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable athena-bot
sudo systemctl start athena-bot
sudo systemctl status athena-bot
```

View logs: `sudo journalctl -u athena-bot -f`

## 📊 Monitoring

### Check Bot Status

1. **Discord**: Use `!status` command in your Discord server
2. **Logs**: `tail -f bot.log` or check screen session
3. **Database**: `sqlite3 trading_data/performance.db "SELECT * FROM trades ORDER BY entry_time DESC LIMIT 10;"`

### Discord Commands

Available commands in your Discord server:
- `!status` - Current bot status and active positions
- `!stats` - Performance statistics (today + all-time)
- `!positions` - List all open positions
- `!stop` - Emergency stop (closes all positions)

### Performance Monitoring

Daily reports automatically sent every 24 hours to reports channel (1432616229159571476):
- Today's performance
- Win rate
- Total P&L
- Active positions
- All-time statistics

## 🔧 Troubleshooting

### Bot Won't Start

**Error: "ModuleNotFoundError"**
```bash
pip3 install -r requirements.txt
```

**Error: "Invalid Discord token"**
```bash
nano .env
# Verify DISCORD_TOKEN is correct
```

**Error: "Binance connection failed"**
```bash
# Check API keys in .env
# Verify USE_TESTNET=true for testnet
```

### Bot Disconnects

Check if bot-hosting.net has:
- Sufficient memory (bot uses ~100-200 MB)
- Network connectivity
- No firewall blocking Discord/Binance APIs

### No Signals Appearing

Normal behavior:
- Bot scans every 15 minutes
- Only executes 3+ star signals (MODERATE or higher)
- Market conditions may not produce signals for hours
- Testnet may have different price feed

Check with `!status` command to see last scan time.

### Database Issues

**Reset database** (WARNING: loses all history):
```bash
rm trading_data/performance.db
python3 auto_trader.py  # Will recreate
```

**Backup database**:
```bash
cp trading_data/performance.db trading_data/performance_backup_$(date +%Y%m%d).db
```

## 📈 Performance Expectations

Based on 30-90 day backtests:

- **Win Rate**: 50-60% expected
- **Average Trades**: 10-20 per week (4 symbols, 15min scans)
- **Position Size**: $100 per trade (adjustable in `auto_trader.py`)
- **Max Positions**: 3 concurrent (adjustable)
- **Best Symbol**: BTCUSDT (60% win rate in tests)

See `WIN_RATE_ANALYSIS.md` for detailed statistics.

## 🔄 Updating Bot

### Pull Latest from GitHub

```bash
cd /bot
git pull origin main
pip3 install -r requirements.txt  # If dependencies changed
# Restart bot (Ctrl+C or systemctl restart)
python3 auto_trader.py
```

### Manual File Updates

Use SFTP to upload modified files, then restart bot.

## 🛡️ Security Recommendations

1. **API Keys**: Use testnet initially, never commit to GitHub
2. **Discord Token**: Keep in `.env` file only
3. **Database Backups**: Regular backups of `performance.db`
4. **Monitor Logs**: Check for unusual activity
5. **Start Small**: Test with $100 positions on testnet first
6. **2FA**: Enable on Binance account when going live

## 🎯 Going Live (After Testing)

After 2-4 weeks of successful testnet operation:

1. **Verify Performance**:
   ```bash
   sqlite3 trading_data/performance.db "SELECT COUNT(*), AVG(pnl_percent), SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate FROM trades WHERE status = 'closed';"
   ```
   Should show >50% win rate, >30 trades

2. **Update to Mainnet**:
   ```bash
   nano .env
   # Change: USE_TESTNET=false
   # Update: BINANCE_API_KEY and BINANCE_API_SECRET to LIVE keys
   ```

3. **Restart Bot**:
   ```bash
   # Stop current instance
   python3 auto_trader.py  # Verify "Connected to Binance Futures MAINNET"
   ```

4. **Start with Small Positions**: Adjust `position_size_usdt` in `auto_trader.py` (line 303)

## 📞 Support

- **Documentation**: See `/bot/docs/` for comprehensive guides
- **GitHub Issues**: https://github.com/studiocz-dev/athena_v2/issues
- **Configuration**: `CONFIGURATION.md`
- **MTF Guide**: `MTF_OPTIMIZATION_GUIDE.md`

## ⚠️ Important Notes

1. **Testnet First**: Always test thoroughly on testnet before live trading
2. **24/7 Operation**: Bot runs continuously, monitor via Discord
3. **Risk Management**: Built-in stop losses (ATR-based)
4. **Max Positions**: Limited to 3 concurrent (prevents overexposure)
5. **Database**: SQLite stores all trades, back up regularly
6. **Channel IDs**: Pre-configured for your Discord channels
7. **Emergency Stop**: Use `!stop` command to close all positions immediately

## 🎉 Success Checklist

- [ ] Files uploaded to `/bot` directory
- [ ] `.env` file created with correct API keys
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] Test setup passed (`python3 test_setup.py`)
- [ ] Bot started successfully (screen/nohup/systemd)
- [ ] Bot logged into Discord as FutureBot#6502
- [ ] Background tasks running (scan, check, report)
- [ ] Signals channel configured (1423658108286275717)
- [ ] Reports channel configured (1432616229159571476)
- [ ] `!status` command works in Discord
- [ ] First scan completed without errors

---

**Ready to deploy?** Run `.\deploy_to_bothosting.ps1` from your local machine! 🚀
