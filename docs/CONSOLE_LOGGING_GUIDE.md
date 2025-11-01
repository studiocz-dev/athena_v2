# 📊 Console Logging Guide

## Overview

The bot now has **detailed, colorful console logging** to show you exactly what's happening in real-time. Every action is logged with clear indicators and formatting.

---

## 🚀 Startup Logs

When you run `python run_bot.py`, you'll see:

```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
ATHENA V2 - AUTOMATED TRADING BOT
Starting initialization...
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

2025-11-01 15:30:00 - BinanceClient - INFO - Connected to Binance Futures TESTNET
2025-11-01 15:30:00 - AutoTrader - INFO - Performance database initialized: trading_data/performance.db
2025-11-01 15:30:00 - AutoTrader - INFO - ✅ Automated Trading Bot initialized
2025-11-01 15:30:00 - AutoTrader - INFO - ✅ Bot instance created successfully

============================================================
🤖 ATHENA V2 AUTOMATED TRADING BOT
============================================================
✅ Bot logged in as: FutureBot#6502
📊 Watchlist: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT
⭐ Min Signal Stars: 3
💰 Position Size: $100 per trade
📈 Max Positions: 3
⏰ Scan Frequency: Every 15 minutes
🎯 Position Check: Every 5 minutes
📊 Daily Report: Every 24 hours
📢 Signals Channel: #trading-signals
📊 Reports Channel: #performance-reports

🔄 Starting background tasks...
✅ Scan & Trade task started (15 min interval)
✅ Position Check task started (5 min interval)
✅ Daily Report task started (24 hour interval)

🚀 Bot is now running and monitoring markets!
============================================================
```

---

## 🔍 Scanning Logs (Every 15 minutes)

```
============================================================
🔍 SCANNING WATCHLIST FOR TRADING SIGNALS
⏰ Scan Time: 2025-11-01 15:45:00
📊 Symbols: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT
📈 Open Positions: 1/3

📌 [1/4] Analyzing BTCUSDT...
   Signal: BUY ⭐⭐⭐⭐ (4 stars)
   Price: $67850.2500
   ✅ VALID SIGNAL! Executing BUY trade...
   
------------------------------------------------------------
🎯 EXECUTING TRADE
Symbol: BTCUSDT
Signal: BUY ⭐⭐⭐⭐
Entry Price: $67850.2500
Position Size: 0.001 BTCUSDT ($67.85)
Stop Loss: $67200.0000 (-0.96%)
Take Profit: $69500.0000 (+2.43%)
Risk/Reward: 2.54

📤 Placing BUY order on TESTNET...
✅ Trade #42 executed successfully!
💾 Trade saved to database
------------------------------------------------------------

📌 [2/4] Analyzing ETHUSDT...
   Signal: HOLD ⭐⭐ (2 stars)
   Price: $2645.3200
   ⏸️  No trade signal (HOLD)
   
📌 [3/4] Analyzing BNBUSDT...
   Signal: SELL ⭐⭐ (2 stars)
   Price: $598.4500
   ⚠️  Signal below threshold (2 < 3 stars)
   
📌 [4/4] Analyzing SOLUSDT...
   Signal: BUY ⭐⭐⭐⭐⭐ (5 stars)
   Price: $185.2300
   ℹ️  Already have open position in SOLUSDT, skipping

✅ Scan complete: 1 valid signal(s) found
============================================================
```

---

## 🎯 Position Check Logs (Every 5 minutes)

```
============================================================
🎯 CHECKING POSITIONS - 2 open
⏰ Check Time: 2025-11-01 15:50:00

📊 [1/2] BTCUSDT (BUY)
   Entry: $67850.2500
   Current: $68200.5000 🟢 (+0.52%)
   TP: $69500.0000 (1.91% away)
   SL: $67200.0000 (1.47% away)
   ⏳ Position still open

📊 [2/2] SOLUSDT (BUY)
   Entry: $185.2300
   Current: $187.8500 🟢 (+1.41%)
   TP: $189.5000 (0.88% away)
   SL: $183.0000 (2.58% away)
   🎯 TP HIT! Closing position...
   ✅ Position closed: P&L = $+2.62 (+1.41%)

✅ Position check complete
============================================================
```

---

## 📊 Daily Report Logs (Every 24 hours)

```
============================================================
📊 GENERATING DAILY PERFORMANCE REPORT
⏰ Report Time: 2025-11-02 00:00:00

Today's Stats:
- Total Trades: 8
- Winning Trades: 5
- Losing Trades: 3
- Win Rate: 62.5%
- Total P&L: $+42.50

All-Time Stats:
- Total Trades: 156
- Win Rate: 58.3%
- Total P&L: $+234.80

✅ Daily report sent to Discord
============================================================
```

---

## 🛑 Emergency Stop Logs

```
⚠️  🛑 EMERGENCY STOP requested by User#1234
🛑 Closed BTCUSDT at $68150.5000
🛑 Closed ETHUSDT at $2652.3000
🛑 Emergency stop complete: 2 positions closed
```

---

## 📝 Log Emoji Legend

| Emoji | Meaning |
|-------|---------|
| 🚀 | Startup / Launch |
| ✅ | Success / Complete |
| ❌ | Error / Failed |
| ⚠️  | Warning / Alert |
| 🔍 | Scanning / Searching |
| 📊 | Statistics / Data |
| 📈 | Trading / Positions |
| 🎯 | Target Hit / Action |
| 💰 | Money / Value |
| ⭐ | Signal Strength |
| 🟢 | Profit / Green |
| 🔴 | Loss / Red |
| ⏰ | Time / Schedule |
| 📢 | Notification / Alert |
| 🛑 | Stop / Emergency |
| ℹ️  | Information |
| 🔄 | Processing / Loop |
| 💾 | Database / Storage |
| 🤖 | Bot / System |
| ⏳ | Waiting / Pending |
| ⏸️  | Hold / Pause |

---

## 🎨 Log Levels

The bot uses standard Python logging levels:

- **DEBUG**: Detailed diagnostic info (disabled by default)
- **INFO**: General informational messages (main logs)
- **WARNING**: Warning messages (yellow)
- **ERROR**: Error messages with stack traces (red)

---

## 📍 What's Logged

### Startup:
- ✅ Binance connection (TESTNET/MAINNET)
- ✅ Database initialization
- ✅ Bot login
- ✅ Discord channel detection
- ✅ Background task start

### Every Scan (15 min):
- ✅ Scan start time
- ✅ Current open positions count
- ✅ Each symbol analysis result
- ✅ Signal strength (stars)
- ✅ Current price
- ✅ Trade execution details
- ✅ Position size and risk/reward

### Position Checks (5 min):
- ✅ Number of open positions
- ✅ Current price for each position
- ✅ Unrealized P&L %
- ✅ Distance to TP/SL
- ✅ Position closures (TP/SL hit)
- ✅ Realized P&L

### Daily Reports:
- ✅ Today's performance
- ✅ All-time statistics
- ✅ Win rate
- ✅ Total P&L

### Discord Commands:
- ✅ !status - Bot status requested
- ✅ !report - Manual report generated
- ✅ !stop - Emergency stop executed

---

## 🔧 Customizing Logs

### Change Log Level

Edit `src/logger.py`:

```python
# For more detailed logs:
logging.basicConfig(level=logging.DEBUG)

# For fewer logs:
logging.basicConfig(level=logging.WARNING)
```

### Log to File

The bot automatically logs to `logs/` directory with rotation:
- `logs/bot.log` - Current log file
- Rotates at 10MB
- Keeps last 5 log files

---

## 📖 Example Full Console Output

See above sections for detailed examples of each log type.

### Tips:
1. **Redirect to file**: `python run_bot.py > bot_output.txt 2>&1`
2. **Watch logs**: `tail -f logs/bot.log` (Linux/Mac)
3. **Search logs**: `grep "ERROR" logs/bot.log`
4. **Filter by date**: `grep "2025-11-01" logs/bot.log`

---

## 🎯 Monitoring Best Practices

1. **Watch startup logs** - Ensure all components initialize
2. **Check scan results** - Verify signals are being detected
3. **Monitor position checks** - Track unrealized P&L
4. **Review error logs** - Fix any issues immediately
5. **Analyze daily reports** - Track performance trends

---

**Your bot now provides comprehensive, real-time console feedback!** 🚀📊
