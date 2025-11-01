# 🎯 Quick Backtest Commands

## Run a Backtest

### Option 1: Interactive (Choose settings)
```powershell
python backtest.py
```

### Option 2: Quick Test (EMA_CROSS on BTC)
```powershell
python batch_backtest.py quick
```

### Option 3: Batch Test (All strategies)
```powershell
python batch_backtest.py
```

---

## Example Output

```
💰 PERFORMANCE:
  Initial Capital: $10,000.00
  Final Capital:   $11,250.00
  Total Return:    +12.50%

📈 TRADES:
  Total Trades: 25
  Winning: 16 (64.0%)
  Losing:  9 (36.0%)

📊 STATISTICS:
  Avg Win:  +3.50%
  Avg Loss: -1.80%
  Profit Factor: 1.94
  Max Drawdown:  -8.50%
```

---

## What's Good?

✅ **Return:** >10%  
✅ **Win Rate:** >50%  
✅ **Profit Factor:** >1.5  
✅ **Max Drawdown:** <20%  

---

## Quick Tips

- Test 30 days minimum
- Compare multiple strategies
- Lower timeframe = more trades
- Higher signal strength = fewer trades
- Always test before live trading!

---

**Start Testing Now!**
```powershell
python batch_backtest.py quick
```
