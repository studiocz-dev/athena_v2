# Quick Start Guide for Athena Trading Bot

## 🚀 5-Minute Setup

### Step 1: Install Python Dependencies (1 min)

```powershell
pip install -r requirements.txt
```

### Step 2: Configure Environment (2 min)

1. Copy `.env.example` to `.env`
2. Fill in required values:

```env
# REQUIRED - Get from Discord Developer Portal
DISCORD_BOT_TOKEN=your_token_here

# REQUIRED - Get from Binance API Management
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here

# OPTIONAL - For testnet (recommended for testing)
BINANCE_TESTNET=True

# OPTIONAL - Adjust trading parameters
DEFAULT_LEVERAGE=5
DEFAULT_ORDER_SIZE_USDT=50
```

### Step 3: Run the Bot (1 min)

```powershell
python bot.py
```

You should see:
```
✅ Bot logged in as YourBot#1234
✅ Connected to Binance Futures
```

### Step 4: Test in Discord (1 min)

In your Discord server, try:

```
/help
/signal symbol:BTCUSDT
/price symbol:BTCUSDT
```

---

## 📋 Checklist

- [ ] Python 3.9+ installed
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] Discord bot created and invited to server
- [ ] Binance API keys generated
- [ ] `.env` file configured
- [ ] Bot running successfully
- [ ] Commands responding in Discord

---

## 🔧 Common Issues

### Bot won't start
```powershell
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Discord commands not working
- Enable "Message Content Intent" in Discord Developer Portal
- Make sure bot has proper permissions
- Restart the bot

### Binance connection error
- Check API keys are correct
- Enable "Futures" permission on API key
- Try with `BINANCE_TESTNET=True` first

---

## 📖 Next Steps

1. **Test with Testnet:**
   - Set `BINANCE_TESTNET=True`
   - Get free testnet funds
   - Test all features

2. **Try Different Strategies:**
   ```
   /strategies  # See all available
   /signal symbol:ETHUSDT strategy:MACD_SIGNAL
   /scan strategy:TRIPLE_EMA min_strength:60
   ```

3. **Enable Monitoring:**
   ```
   /monitor action:start channel:#signals
   ```

4. **Check Account:**
   ```
   /balance
   /positions
   ```

---

## 🎯 Recommended Settings for Beginners

```env
# Conservative settings
DEFAULT_LEVERAGE=3
DEFAULT_ORDER_SIZE_USDT=50
DEFAULT_RISK_PERCENTAGE=1.0
MAX_POSITIONS=2
TRADING_ENABLED=False  # Manual trading only
```

Start with:
- Low leverage (3-5x)
- Small position sizes
- Testnet first
- Paper trade for 1-2 weeks
- Keep a trading journal

---

## 📚 Learning Resources

### Strategy Tutorials
- `/strategies` - List all strategies in bot
- Try each strategy with `/signal` command
- Compare results across different timeframes

### Risk Management
- Never risk >1-2% per trade
- Use stop losses always
- Start small and scale up
- Track your win rate

### Discord Commands
- `/help` - All commands
- `/signal` - Get trading signal
- `/scan` - Scan multiple symbols
- `/monitor` - Auto signal updates

---

## ⚠️ Remember

1. **Start with TESTNET** - `BINANCE_TESTNET=True`
2. **Use LOW LEVERAGE** - 3-5x max for beginners
3. **Small position sizes** - $50-100 to start
4. **Always use stop losses** - Protect your capital
5. **Paper trade first** - Practice makes perfect

---

## 🆘 Need Help?

1. Read the full README.md
2. Check Troubleshooting section
3. Review Binance API documentation
4. Test with smaller amounts first
5. Open an issue on GitHub

---

**Good luck and trade responsibly! 🚀**
