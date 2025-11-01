# Configuration Guide for Athena Trading Bot

## 📋 Complete Configuration Reference

This guide explains every configuration option available in the Athena Trading Bot.

---

## 🔧 Environment Variables (.env)

### Discord Configuration

```env
# Your Discord Bot Token from Discord Developer Portal
# Get it from: https://discord.com/developers/applications
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Your Discord Server (Guild) ID
# Enable Developer Mode in Discord → Right-click server → Copy Server ID
DISCORD_GUILD_ID=123456789012345678

# Channel ID where automatic signals will be posted
# Right-click channel → Copy Channel ID
SIGNAL_CHANNEL_ID=123456789012345678
```

### Binance API Configuration

```env
# Your Binance API Key
# Create at: Binance → Profile → API Management
BINANCE_API_KEY=your_binance_api_key_here

# Your Binance API Secret
BINANCE_API_SECRET=your_binance_api_secret_here

# Use Binance Testnet (recommended for testing)
# True = Testnet (paper trading), False = Real trading
BINANCE_TESTNET=True
```

**⚠️ API Key Permissions Required:**
- ✅ Enable Reading
- ✅ Enable Futures
- ❌ Disable Withdrawals (for safety)

### Trading Configuration

```env
# Default leverage for new positions (1-125)
# Recommendation: Start with 3-5x for beginners
DEFAULT_LEVERAGE=10

# Default order size in USDT
# This is the margin amount, not the position size
# With 10x leverage, $100 margin = $1000 position
DEFAULT_ORDER_SIZE_USDT=100

# Risk percentage per trade (0.1-5.0)
# 1.0 = risk 1% of account per trade
DEFAULT_RISK_PERCENTAGE=1.0

# Maximum number of concurrent positions (1-10)
# Limits how many trades can be open at once
MAX_POSITIONS=3
```

### Bot Settings

```env
# Enable actual trading (True/False)
# False = Signals only, no trading
# True = Bot can execute trades
TRADING_ENABLED=False

# Logging level (DEBUG, INFO, WARNING, ERROR)
# DEBUG = Most verbose, ERROR = Least verbose
LOG_LEVEL=INFO
```

---

## ⚙️ Configuration File (config.py)

### Trading Intervals

Available timeframes for analysis:

```python
VALID_INTERVALS = [
    '1m',   # 1 minute
    '3m',   # 3 minutes
    '5m',   # 5 minutes
    '15m',  # 15 minutes (default)
    '30m',  # 30 minutes
    '1h',   # 1 hour
    '2h',   # 2 hours
    '4h',   # 4 hours
    '6h',   # 6 hours
    '12h',  # 12 hours
    '1d'    # 1 day
]
```

**Recommended Intervals by Trading Style:**
- Scalping: 1m, 3m, 5m
- Day Trading: 15m, 30m, 1h
- Swing Trading: 4h, 6h, 12h
- Position Trading: 1d

### Risk Management Settings

```python
# Stop Loss: Distance from entry price
DEFAULT_STOP_LOSS_PERCENTAGE = 2.0  # 2% from entry

# Take Profit: Distance from entry price
DEFAULT_TAKE_PROFIT_PERCENTAGE = 4.0  # 4% from entry

# This creates a 2:1 Risk/Reward ratio
# Risk $100 to make $200
```

**Risk/Reward Examples:**

| Stop Loss | Take Profit | R:R Ratio |
|-----------|-------------|-----------|
| 1%        | 2%          | 1:2       |
| 2%        | 4%          | 1:2       |
| 2%        | 6%          | 1:3       |
| 3%        | 9%          | 1:3       |

### Technical Indicator Periods

```python
# EMA (Exponential Moving Average) periods
EMA_FAST = 9     # Fast EMA
EMA_SLOW = 21    # Slow EMA
EMA_TREND = 50   # Trend EMA

# RSI (Relative Strength Index)
RSI_PERIOD = 14

# MACD (Moving Average Convergence Divergence)
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Stochastic
STOCH_PERIOD = 14
STOCH_SMOOTH = 3
```

**Customization Tips:**
- Shorter periods = More signals, more noise
- Longer periods = Fewer signals, more reliable
- Test different settings with backtesting

### Signal Thresholds

```python
# RSI Levels
RSI_OVERSOLD = 30   # Buy signal threshold
RSI_OVERBOUGHT = 70 # Sell signal threshold

# Stochastic Levels
STOCH_OVERSOLD = 20   # Buy signal threshold
STOCH_OVERBOUGHT = 80 # Sell signal threshold
```

**Aggressive vs Conservative:**

**Aggressive (More Signals):**
```python
RSI_OVERSOLD = 40
RSI_OVERBOUGHT = 60
STOCH_OVERSOLD = 30
STOCH_OVERBOUGHT = 70
```

**Conservative (Fewer, Stronger Signals):**
```python
RSI_OVERSOLD = 25
RSI_OVERBOUGHT = 75
STOCH_OVERSOLD = 15
STOCH_OVERBOUGHT = 85
```

---

## 📊 Strategy Selection

### Available Strategies

Edit in your commands to use different strategies:

```python
AVAILABLE_STRATEGIES = [
    'EMA_CROSS',           # Best for trending markets
    'RSI_DIVERGENCE',      # Best for reversals
    'MACD_SIGNAL',         # Best for momentum
    'STOCH_RSI',           # Best for ranging markets
    'TRIPLE_EMA',          # Best for strong trends
    'BREAKOUT',            # Best for volatility
    'SUPPORT_RESISTANCE'   # Best for ranging markets
]
```

### Strategy Configuration

Each strategy can be customized in `strategies.py`:

**EMA Crossover:**
```python
EMACrossStrategy(fast_period=9, slow_period=21)
```

**Triple EMA:**
```python
TripleEMAStrategy(fast=9, medium=21, slow=50)
```

**RSI:**
```python
RSIDivergenceStrategy(rsi_period=14)
```

**MACD:**
```python
MACDStrategy(fast=12, slow=26, signal=9)
```

**Stochastic RSI:**
```python
StochRSIStrategy(period=14, smooth1=3, smooth2=3)
```

**Breakout:**
```python
BreakoutStrategy(lookback=20)
```

---

## 🎯 Trading Symbols

### Default Tracked Symbols

Edit `bot.py` to change tracked symbols:

```python
self.tracked_symbols = [
    'BTCUSDT',   # Bitcoin
    'ETHUSDT',   # Ethereum
    'BNBUSDT',   # Binance Coin
    'SOLUSDT',   # Solana
    'XRPUSDT',   # Ripple
    'ADAUSDT',   # Cardano
    'DOGEUSDT',  # Dogecoin
    'MATICUSDT', # Polygon
    'DOTUSDT',   # Polkadot
    'LINKUSDT'   # Chainlink
]
```

**Popular Additions:**
- AVAXUSDT (Avalanche)
- ATOMUSDT (Cosmos)
- NEARUSDT (Near Protocol)
- FTMUSDT (Fantom)
- APTUSDT (Aptos)
- ARBUSDT (Arbitrum)
- OPUSDT (Optimism)

---

## 🔔 Monitoring Configuration

### Signal Monitoring Settings

In `bot.py`, adjust the monitoring interval:

```python
@tasks.loop(minutes=15)  # Check every 15 minutes
async def monitor_signals(self):
    ...
```

**Options:**
- Every 5 minutes: `@tasks.loop(minutes=5)`
- Every 30 minutes: `@tasks.loop(minutes=30)`
- Every hour: `@tasks.loop(hours=1)`

### Signal Filtering

Adjust minimum signal strength:

```python
# In monitor_signals() function
signals = self.signal_analyzer.scan_multiple_symbols(
    self.tracked_symbols,
    'EMA_CROSS',
    config.DEFAULT_INTERVAL,
    min_signal_strength=60.0  # Only signals >60% strength
)
```

---

## 🗄️ Database Configuration

### Database Location

```python
DATABASE_PATH = 'trading_data/athena_bot.db'
```

The database stores:
- Trade history
- Signal history
- Performance metrics
- User settings

---

## 📝 Logging Configuration

### Log Files

```python
# Log file location
LOG_FILE = 'logs/athena_bot.log'

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

### Log Levels

Set in `.env`:

**DEBUG:** Everything (very verbose)
```env
LOG_LEVEL=DEBUG
```

**INFO:** General information (default)
```env
LOG_LEVEL=INFO
```

**WARNING:** Only warnings and errors
```env
LOG_LEVEL=WARNING
```

**ERROR:** Only errors
```env
LOG_LEVEL=ERROR
```

---

## 🛠️ Advanced Configuration

### Position Sizing Formula

The bot calculates position size as:

```python
notional_value = order_size_usdt * leverage
quantity = notional_value / current_price
```

**Example:**
- Order Size: $100 USDT
- Leverage: 10x
- BTC Price: $50,000
- Position Size: ($100 × 10) / $50,000 = 0.02 BTC

### Risk Per Trade

```python
risk_amount = account_balance * (risk_percentage / 100)
position_size = risk_amount / (stop_loss_percentage / 100)
```

**Example:**
- Account: $1,000
- Risk: 2%
- Stop Loss: 2%
- Risk Amount: $20
- Max Position: $1,000

---

## 📚 Configuration Templates

### Conservative (Low Risk)

```env
DEFAULT_LEVERAGE=3
DEFAULT_ORDER_SIZE_USDT=50
DEFAULT_RISK_PERCENTAGE=0.5
MAX_POSITIONS=2
```

### Moderate (Balanced)

```env
DEFAULT_LEVERAGE=10
DEFAULT_ORDER_SIZE_USDT=100
DEFAULT_RISK_PERCENTAGE=1.0
MAX_POSITIONS=3
```

### Aggressive (High Risk)

```env
DEFAULT_LEVERAGE=20
DEFAULT_ORDER_SIZE_USDT=200
DEFAULT_RISK_PERCENTAGE=2.0
MAX_POSITIONS=5
```

**⚠️ Warning:** Aggressive settings can lead to significant losses!

---

## 🔐 Security Best Practices

1. **Never share your .env file**
2. **Use IP whitelist on Binance API**
3. **Disable withdrawal permissions**
4. **Start with testnet**
5. **Use 2FA on Binance account**
6. **Store API keys securely**
7. **Regularly rotate API keys**
8. **Monitor API usage**

---

## 📊 Performance Optimization

### For Faster Signals

```python
# Reduce data fetched
limit = 200  # Instead of 500

# Use shorter timeframes
interval = '5m'  # Instead of '15m'

# Cache results (advanced)
```

### For Better Accuracy

```python
# Increase data fetched
limit = 1000

# Use longer timeframes
interval = '1h'

# Multiple strategy confirmation
```

---

## 🆘 Troubleshooting Configuration

### Bot not responding?

Check:
```env
LOG_LEVEL=DEBUG  # Enable debug logging
```

### Too many false signals?

Adjust:
```python
min_signal_strength=70.0  # Increase threshold
RSI_OVERSOLD = 25  # More extreme levels
```

### Not enough signals?

Adjust:
```python
min_signal_strength=40.0  # Lower threshold
RSI_OVERSOLD = 40  # Less extreme levels
```

---

## 📝 Configuration Checklist

- [ ] .env file created and configured
- [ ] Discord bot token added
- [ ] Binance API keys added
- [ ] Leverage set appropriately
- [ ] Risk percentage configured
- [ ] Log level set
- [ ] Testnet enabled (for testing)
- [ ] Tracked symbols defined
- [ ] Strategy preferences set
- [ ] Signal thresholds adjusted
- [ ] Monitoring interval configured

---

**Need help? Read the full README.md or open an issue on GitHub!**
