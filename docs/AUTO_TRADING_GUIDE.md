# 🚀 Automated Trading System - Quick Start Guide

## What This Does

The automated trading system will:
- ✅ **Monitor** BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT every 15 minutes
- ✅ **Analyze** with multi-timeframe analysis (15m + 1h + 4h)
- ✅ **Filter** only 3+ star signals (high quality)
- ✅ **Send** signal alerts to Discord with entry/SL/TP
- ✅ **Execute** trades automatically on testnet
- ✅ **Track** all positions and check for TP/SL every 5 minutes
- ✅ **Report** daily performance summary every 24 hours

---

## 📦 Setup (5 Minutes)

### Step 1: Set Discord Channel IDs

The bot needs to know where to send signals and reports.

**Option A: Use Commands (Recommended)**
1. Start the bot: `python auto_trader.py`
2. In your Discord signals channel, type: `!set_signals_channel`
3. In your Discord reports channel, type: `!set_reports_channel`

**Option B: Hardcode (Alternative)**
Edit `auto_trader.py` line ~255:
```python
self.signals_channel_id = 1234567890  # Your signals channel ID
self.reports_channel_id = 1234567890  # Your reports channel ID
```

### Step 2: Verify Testnet is Active

Check your `.env` file:
```
BINANCE_TESTNET=True  # ← Make sure this is True!
```

### Step 3: Run the Bot

```bash
python auto_trader.py
```

You should see:
```
Bot logged in as YourBot#1234
Background tasks started
Scanning watchlist for signals...
```

---

## 🎯 Bot Behavior

### What Signals Get Traded?

Only signals that meet ALL criteria:
- ✅ Signal is BUY or SELL (not HOLD)
- ✅ Signal strength is 3+ stars (MODERATE or higher)
- ✅ No existing position in that symbol
- ✅ Less than 3 total open positions

### Position Limits

- **Max Positions:** 3 at a time
- **Position Size:** $100 per trade
- **Risk Management:** Automatic SL/TP on every trade

### Monitoring Schedule

| Task | Frequency | Description |
|------|-----------|-------------|
| **Scan Watchlist** | Every 15 min | Check all symbols for signals |
| **Check Positions** | Every 5 min | Monitor TP/SL hits |
| **Daily Report** | Every 24 hours | Performance summary |

---

## 📊 Discord Notifications

### 1. Signal Alerts (When Trade Opened)

```
🟢 BUY Signal - BTCUSDT
⭐⭐⭐⭐ Signal Strength: STRONG

Entry Price: $67,250.00
Stop Loss:   $66,500.00
Take Profit: $68,750.00

Trend Analysis:
Overall: BULLISH
HTF Confirmation: ✅

Recommendation: Good BUY opportunity with higher timeframe confirmation. Consider entering.

Order placed on Testnet | Auto-Trading Active
```

### 2. Exit Notifications (When Trade Closed)

```
✅ Trade Closed - BTCUSDT
Exit Reason: TP

P&L: $45.32
Return: 2.15%

Testnet Trading
```

### 3. Daily Performance Reports (Every 24 Hours)

```
📊 Daily Performance Report
Report for 2025-11-01

📈 Today's Performance
Trades: 5
Won: 3 | Lost: 2
Win Rate: 60.0%
Total P&L: 🟢 $156.78
Best Trade: $85.23
Worst Trade: -$42.15

🏆 All-Time Statistics
Total Trades: 15
Win Rate: 53.3%
Total P&L: 🟢 $423.56
Avg Win: $75.12
Avg Loss: -$38.45
Best Trade: $125.67
Worst Trade: -$65.23

💼 Open Positions (2)
ETHUSDT BUY @ $2,456.78 (4⭐)
BNBUSDT BUY @ $312.45 (3⭐)
```

---

## 🛠️ Bot Commands

Use these commands in Discord:

```
!set_signals_channel  - Set current channel for signal alerts
!set_reports_channel  - Set current channel for daily reports
!status               - Get current bot status
!report               - Generate performance report immediately
```

---

## ⚙️ Configuration

Edit `auto_trader.py` to customize:

```python
# Line ~249-252: Watchlist
self.watchlist = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']
# Add/remove symbols as needed

# Line ~254-256: Trading settings
self.min_signal_stars = 3     # Min star rating (1-5)
self.position_size_usdt = 100 # $ per trade
self.max_positions = 3        # Max concurrent positions
```

### Recommended Settings:

**Conservative:**
```python
self.min_signal_stars = 4      # Only 4-5 star signals
self.position_size_usdt = 50   # $50 per trade
self.max_positions = 2         # Max 2 positions
```

**Balanced (Default):**
```python
self.min_signal_stars = 3      # 3+ star signals
self.position_size_usdt = 100  # $100 per trade
self.max_positions = 3         # Max 3 positions
```

**Aggressive:**
```python
self.min_signal_stars = 2      # 2+ star signals
self.position_size_usdt = 200  # $200 per trade
self.max_positions = 5         # Max 5 positions
```

---

## 📁 Database

All trades are stored in: `trading_data/performance.db`

Tables:
- `trades` - All trades with entry, exit, P&L
- `daily_stats` - Daily performance summaries

View with SQLite browser or Python:
```python
import sqlite3
conn = sqlite3.connect('trading_data/performance.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM trades")
for trade in cursor.fetchall():
    print(trade)
```

---

## 🔍 Monitoring

### Check if Bot is Running

Look for these log messages:
```
Bot logged in as YourBot#1234
Background tasks started
Scanning watchlist for signals...
Checking 0 open positions...
```

### Check Database

```bash
# Windows PowerShell
python -c "import sqlite3; conn = sqlite3.connect('trading_data/performance.db'); print(conn.execute('SELECT COUNT(*) FROM trades').fetchone())"
```

### Test Immediately

Force a scan without waiting 15 minutes:
1. Stop the bot (Ctrl+C)
2. Change scan frequency to 1 minute (line ~270):
   ```python
   @tasks.loop(minutes=1)  # Was 15
   ```
3. Restart bot
4. Watch for signals within 1 minute

---

## 🚨 Troubleshooting

### No Signals Appearing

**Possible causes:**
1. No 3+ star signals in current market
2. Already have max positions (3)
3. Already have position in that symbol

**Solution:** Lower min_signal_stars to 2 or check status:
```
!status
```

### Bot Not Sending to Discord

**Possible causes:**
1. Channel IDs not set
2. Bot doesn't have permission to send messages

**Solution:**
```
!set_signals_channel
!set_reports_channel
```

Make sure bot has "Send Messages" and "Embed Links" permissions.

### Database Errors

**Solution:** Delete and recreate:
```bash
rm trading_data/performance.db
python auto_trader.py
```

### Position Not Closing

**Possible causes:**
1. Price hasn't hit SL/TP yet
2. Check frequency is 5 minutes (be patient)

**Solution:** Check current price vs SL/TP:
```
!status
```

---

## 📈 Expected Performance

Based on our backtesting:

### Week 1 (Learning Phase):
- **Signals:** 5-10 signals
- **Trades:** 3-6 trades (with max 3 positions limit)
- **Expected Return:** -5% to +10%
- **Goal:** Validate system works correctly

### Week 2-4 (Data Collection):
- **Signals:** 15-30 signals
- **Trades:** 10-20 trades
- **Expected Return:** 0% to +15%
- **Goal:** Collect 30+ trades for statistics

### After 30 Trades:
- Calculate real win rate
- Compare to backtest (50-60%)
- Adjust strategy if needed

---

## 🎯 Success Metrics

Track these in daily reports:

| Metric | Target | Status |
|--------|--------|--------|
| Win Rate | >50% | After 30 trades |
| Profit Factor | >2.0 | Monitor weekly |
| Max Drawdown | <10% | Track daily |
| Avg Win/Loss Ratio | >2:1 | After 20 trades |

---

## 🔄 Workflow

### Daily Routine:

**Morning:**
1. Check Discord for overnight signals
2. Review any closed positions
3. Check open positions status

**During Day:**
- Bot runs automatically
- Receives signal alerts
- Watches for exits

**Evening:**
1. Review daily performance report
2. Check if adjustments needed
3. Plan for tomorrow

### Weekly Review:

1. Calculate win rate from database
2. Compare to backtest expectations
3. Adjust min_signal_stars if needed
4. Update watchlist based on performance

---

## 🚀 Going Live (After Paper Trading Success)

Once win rate > 50% for 30+ trades:

1. **Update .env:**
   ```
   BINANCE_TESTNET=False
   ```

2. **Start Small:**
   ```python
   self.position_size_usdt = 50  # Start with $50
   ```

3. **Monitor Closely:**
   - First 10 trades on live
   - Compare to testnet results
   - Gradually increase size

4. **Scale Up:**
   - If profitable after 10 trades
   - Increase to $100, then $200
   - Keep max_positions at 3

---

## 📞 Support

If you need help:
1. Check log files in console
2. Review database with SQLite browser
3. Test with `!status` command
4. Check signal quality with lower min_stars

---

## ⚠️ Important Notes

1. **This is testnet** - No real money at risk
2. **Bot runs 24/7** - Keep computer on or use cloud server
3. **Signals are automatic** - Bot will trade without asking
4. **Monitor daily** - Check reports and adjust as needed
5. **Paper trade for 2-4 weeks** - Don't rush to live trading

---

**Ready to start?**

```bash
python auto_trader.py
```

Then in Discord:
```
!set_signals_channel
!set_reports_channel
!status
```

**The bot is now monitoring markets and will trade automatically!** 🚀
