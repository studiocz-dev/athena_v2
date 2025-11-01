# 📊 Backtesting Guide for Athena Bot

## What is Backtesting?

Backtesting tests your trading strategies against historical market data to see how they would have performed in the past. This helps you:

- ✅ Evaluate strategy performance before risking real money
- ✅ Compare different strategies objectively
- ✅ Understand win rates and risk/reward
- ✅ Optimize parameters
- ✅ Build confidence in your trading approach

---

## 🚀 Quick Start

### Option 1: Interactive Backtest (Recommended for Beginners)

```powershell
# Run interactive backtest
python backtest.py
```

You'll be prompted for:
- Symbol (e.g., BTCUSDT)
- Strategy (choose from 7 options)
- Interval (15m, 1h, 4h, etc.)
- Days back (how much history to test)

**Example:**
```
Symbol: BTCUSDT
Strategy: 1 (EMA_CROSS)
Interval: 15m
Days back: 30
```

### Option 2: Quick Test (Single Command)

```powershell
# Quick test of EMA_CROSS on BTCUSDT
python batch_backtest.py quick
```

### Option 3: Batch Test (Test Multiple Strategies)

```powershell
# Test all strategies on BTC and ETH
python batch_backtest.py
```

This will test:
- 4 strategies (EMA_CROSS, MACD_SIGNAL, RSI_DIVERGENCE, TRIPLE_EMA)
- 2 symbols (BTCUSDT, ETHUSDT)
- Show comprehensive comparison

---

## 📋 Understanding the Results

### Performance Metrics

```
💰 PERFORMANCE:
  Initial Capital: $10,000.00
  Final Capital:   $11,250.00
  Total Return:    +12.50%
```

- **Initial Capital**: Starting balance
- **Final Capital**: Ending balance after all trades
- **Total Return**: Percentage gain/loss

### Trade Statistics

```
📈 TRADES:
  Total Trades: 25
  Winning: 16 (64.0%)
  Losing:  9 (36.0%)
  Long:  13
  Short: 12
```

- **Total Trades**: Number of trades executed
- **Winning/Losing**: Win rate percentage
- **Long/Short**: Trade direction breakdown

### Exit Analysis

```
🎯 EXIT REASONS:
  Take Profit: 14
  Stop Loss:   11
```

- **Take Profit**: Trades that hit profit target
- **Stop Loss**: Trades that hit stop loss

### Risk Metrics

```
📊 STATISTICS:
  Avg Win:  +3.50%
  Avg Loss: -1.80%
  Profit Factor: 1.94
  Max Drawdown:  -8.50%
```

- **Avg Win/Loss**: Average gain per winning/losing trade
- **Profit Factor**: Ratio of gross profit to gross loss (>1 is profitable)
- **Max Drawdown**: Largest peak-to-trough decline

---

## 🎯 What Makes a Good Strategy?

### Excellent Strategy ⭐⭐⭐⭐⭐
- Total Return: >20%
- Win Rate: >55%
- Profit Factor: >2.0
- Max Drawdown: <15%

### Good Strategy ⭐⭐⭐⭐
- Total Return: 10-20%
- Win Rate: 50-55%
- Profit Factor: 1.5-2.0
- Max Drawdown: 15-25%

### Acceptable Strategy ⭐⭐⭐
- Total Return: 5-10%
- Win Rate: 45-50%
- Profit Factor: 1.2-1.5
- Max Drawdown: 25-35%

### Poor Strategy ⭐
- Total Return: <5% or negative
- Win Rate: <45%
- Profit Factor: <1.2
- Max Drawdown: >35%

---

## 💡 Example Results Interpretation

### Example 1: Strong Strategy

```
Strategy: EMA_CROSS on BTCUSDT
Total Return:    +15.50%
Win Rate:        58.3%
Profit Factor:   2.15
Max Drawdown:    -12.00%
Total Trades:    24
```

**Interpretation:** ✅ Excellent! 
- Solid return with good win rate
- Profit factor >2 means wins are much larger than losses
- Drawdown is manageable
- **Verdict: Use this strategy!**

### Example 2: Risky Strategy

```
Strategy: BREAKOUT on ETHUSDT
Total Return:    +8.00%
Win Rate:        42.0%
Profit Factor:   1.35
Max Drawdown:    -28.00%
Total Trades:    31
```

**Interpretation:** ⚠️ Caution!
- Low win rate (more losers than winners)
- Large drawdown could be stressful
- Profit factor acceptable but not great
- **Verdict: Needs optimization or avoid**

### Example 3: Losing Strategy

```
Strategy: RSI_DIVERGENCE on SOLUSDT
Total Return:    -5.50%
Win Rate:        38.0%
Profit Factor:   0.85
Max Drawdown:    -35.00%
Total Trades:    18
```

**Interpretation:** ❌ Poor!
- Negative returns
- Low win rate
- Profit factor <1 (loses more than wins)
- High drawdown
- **Verdict: Don't use this strategy on this symbol**

---

## ⚙️ Customizing Backtest Parameters

### In Python Code

Edit `batch_backtest.py` or call directly:

```python
from backtest import Backtester

backtester = Backtester(initial_capital=10000)

results = backtester.run_backtest(
    symbol='BTCUSDT',
    strategy_name='EMA_CROSS',
    interval='15m',
    days_back=30,
    position_size_pct=10.0,    # 10% of capital per trade
    stop_loss_pct=2.0,         # 2% stop loss
    take_profit_pct=4.0,       # 4% take profit
    min_signal_strength=50.0   # Minimum 50% signal strength
)

backtester.print_results(results)
```

### Parameter Guide

**position_size_pct**: Percentage of capital per trade
- Conservative: 5%
- Moderate: 10%
- Aggressive: 20%

**stop_loss_pct**: Stop loss distance from entry
- Tight: 1%
- Normal: 2%
- Loose: 3-5%

**take_profit_pct**: Take profit distance from entry
- Conservative: 2-3%
- Normal: 4-6%
- Aggressive: 8-10%

**min_signal_strength**: Minimum signal quality
- Strict: 70%+
- Normal: 50-60%
- Loose: 30-40%

---

## 📈 Optimization Tips

### 1. Test Different Timeframes

```powershell
# Test different intervals
python backtest.py
# Try: 15m, 1h, 4h
```

- Lower timeframes (5m, 15m): More trades, more noise
- Higher timeframes (1h, 4h): Fewer trades, stronger signals

### 2. Adjust Stop Loss / Take Profit

Try different risk/reward ratios:
- 1:1 (SL: 2%, TP: 2%)
- 1:2 (SL: 2%, TP: 4%) ← Default
- 1:3 (SL: 2%, TP: 6%)

### 3. Test Multiple Symbols

Different strategies work better on different assets:
- BTC: Usually best with trend-following (EMA, MACD)
- ETH: Good with all strategies
- Altcoins: Often better with RSI, Breakout

### 4. Vary Signal Strength Threshold

```python
# Higher threshold = fewer but stronger signals
min_signal_strength=70.0

# Lower threshold = more signals but weaker
min_signal_strength=40.0
```

---

## 🔍 Analyzing Trade Details

### View Individual Trades

The backtest shows your last 10 trades:

```
📝 LAST 10 TRADES:
Time              Side   Entry      Exit       Reason  P&L
2024-10-25 14:30  LONG   $45,250    $46,035    TP      🟢 +1.73%
2024-10-25 16:45  SHORT  $46,100    $45,178    TP      🟢 +2.00%
2024-10-25 19:00  LONG   $45,200    $44,296    SL      🔴 -2.00%
```

**Understanding:**
- ✅ Green = Winning trade
- ❌ Red = Losing trade
- **TP** = Hit take profit target
- **SL** = Hit stop loss

### Common Patterns

**Good Pattern:**
```
🟢 +2.00% (TP)
🟢 +1.80% (TP)
🔴 -1.50% (SL)
🟢 +2.50% (TP)
```
More greens than reds, wins bigger than losses ✅

**Bad Pattern:**
```
🔴 -2.00% (SL)
🔴 -2.00% (SL)
🟢 +1.20% (TP)
🔴 -2.00% (SL)
```
Too many reds, losses bigger than wins ❌

---

## 📊 Batch Testing Workflow

### Step 1: Run Batch Test

```powershell
python batch_backtest.py
```

### Step 2: Review Rankings

The batch test shows all strategies ranked by performance:

```
Rank   Symbol      Strategy            Return      Win Rate    Trades
1      BTCUSDT     EMA_CROSS          +15.50%     58.3%       24
2      ETHUSDT     MACD_SIGNAL        +12.30%     55.0%       20
3      BTCUSDT     TRIPLE_EMA         +10.20%     52.0%       18
4      ETHUSDT     RSI_DIVERGENCE     +8.50%      48.0%       22
```

### Step 3: Pick Best Performers

Choose top 2-3 strategies:
- ✅ Best return
- ✅ Good win rate (>50%)
- ✅ Decent number of trades (10+)

### Step 4: Test with Different Parameters

Optimize your top strategies:
```python
# Test with tighter stops
stop_loss_pct=1.5

# Test with wider targets  
take_profit_pct=6.0

# Test with stricter signals
min_signal_strength=65.0
```

---

## ⚠️ Important Warnings

### Past Performance ≠ Future Results

**Backtesting shows what WOULD have happened, not what WILL happen.**

- Markets change
- Past patterns may not repeat
- Overfitting can make results look better than reality

### Avoid Overfitting

Don't adjust parameters until you get "perfect" results. This is curve-fitting and won't work in live trading.

**Good Approach:** ✅
- Test standard parameters
- Compare multiple strategies
- Pick one that works well
- Use it as-is

**Bad Approach:** ❌
- Adjust parameters 100 times
- Pick the "perfect" combo
- Expect same results live
- Wonder why it fails

### Market Conditions Matter

A strategy might work in:
- ✅ Trending markets (EMA, MACD)
- ❌ Ranging markets

Or vice versa:
- ✅ Ranging markets (RSI, Support/Resistance)
- ❌ Trending markets

**Solution:** Test in different market conditions (bull, bear, sideways)

---

## 🎯 Recommended Testing Workflow

### Phase 1: Initial Testing (30 minutes)

```powershell
# Quick test all strategies
python batch_backtest.py
```

- Review all results
- Note top 3 performers
- Check which symbols work best

### Phase 2: Deep Dive (1 hour)

```powershell
# Test best strategy with different parameters
python backtest.py
```

Test your top strategy with:
- Different timeframes (15m, 1h, 4h)
- Different periods (7, 14, 30, 60 days)
- Different stop losses (1%, 2%, 3%)

### Phase 3: Validation (1 week)

- Paper trade your best strategy on testnet
- Compare live results to backtest
- Adjust if needed

### Phase 4: Live Trading (Start Small!)

- Begin with smallest position sizes
- Test for 1-2 weeks
- Scale up gradually if profitable

---

## 📁 Result Files

Backtest results are saved to `trading_data/` folder:

```
trading_data/
  backtest_results_20241101_143022.json
  batch_backtest_20241101_145533.json
```

Open these in any text editor to see full details of all trades.

---

## 🔧 Troubleshooting

### "No historical data available"

**Cause:** Binance API connection issue  
**Fix:** 
- Check your `.env` file has correct API keys
- Verify internet connection
- Try with different symbol

### "No trades executed"

**Cause:** Strategy didn't generate any signals  
**Fix:**
- Lower `min_signal_strength` parameter
- Try different timeframe
- Use different strategy

### "Error analyzing candle"

**Cause:** Not enough historical data for indicators  
**Fix:**
- Increase `days_back` parameter
- Use shorter timeframe

---

## 💡 Pro Tips

1. **Test Multiple Timeframes**
   - 15m for day trading
   - 1h for swing trading
   - 4h for position trading

2. **Compare Symbols**
   - BTC usually most reliable
   - ETH good for diversification
   - Altcoins more volatile (higher risk/reward)

3. **Look at Win Rate vs Profit Factor**
   - 40% win rate with 2.5 profit factor = Good ✅
   - 60% win rate with 1.1 profit factor = Risky ⚠️

4. **Check Trade Frequency**
   - Too many trades (>50/month) = Overtrading
   - Too few trades (<5/month) = Underutilized

5. **Consider Drawdown**
   - Can you handle -20% mentally?
   - Lower drawdown = less stress

---

## 🎓 Learning from Results

### High Win Rate, Low Returns

```
Win Rate: 65%
Return: +3%
Profit Factor: 1.2
```

**Problem:** Taking profits too early  
**Solution:** Increase take_profit_pct

### Low Win Rate, High Returns

```
Win Rate: 40%
Return: +18%
Profit Factor: 2.8
```

**Problem:** None! This is actually good  
**Note:** Big wins compensate for more frequent small losses

### Many Stop Losses

```
SL Exits: 18
TP Exits: 7
```

**Problem:** Stop loss too tight or strategy needs work  
**Solution:** Widen stop loss or try different strategy

---

## ✅ Backtest Checklist

Before going live, make sure:

- [ ] Tested multiple strategies
- [ ] Tested multiple symbols
- [ ] Tested multiple timeframes
- [ ] Found strategy with >50% win rate
- [ ] Found strategy with profit factor >1.5
- [ ] Tested over at least 30 days
- [ ] Max drawdown acceptable to you
- [ ] Comfortable with win rate
- [ ] Understand why strategy works
- [ ] Paper traded for 1-2 weeks

---

## 🚀 Ready to Backtest?

```powershell
# Start with quick test
python batch_backtest.py quick

# Then run full batch test
python batch_backtest.py

# Finally test your favorite strategy
python backtest.py
```

**Good luck! 📈**

Remember: Backtesting is essential, but always:
1. Verify on testnet
2. Start small
3. Manage risk
4. Keep learning
