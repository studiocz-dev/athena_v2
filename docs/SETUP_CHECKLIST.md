# 📋 Athena Bot - Complete Setup Checklist

Follow this checklist step-by-step to get your bot running successfully.

---

## Phase 1: Prerequisites ✅

### System Requirements
- [ ] Windows 10/11 (or Linux/Mac)
- [ ] Python 3.9 or higher installed
- [ ] PowerShell or Terminal access
- [ ] Internet connection
- [ ] Text editor (VS Code, Notepad++, etc.)

### Accounts Required
- [ ] Discord account created
- [ ] Binance account created (or testnet account)
- [ ] Email verified on both platforms
- [ ] 2FA enabled on Binance (highly recommended)

---

## Phase 2: Discord Bot Setup 🤖

### Create Discord Application
- [ ] Go to https://discord.com/developers/applications
- [ ] Click "New Application"
- [ ] Name your bot (e.g., "Athena Trading Bot")
- [ ] Accept Terms of Service

### Configure Bot
- [ ] Go to "Bot" section
- [ ] Click "Add Bot"
- [ ] Click "Reset Token" and copy token
- [ ] Save token securely (you'll need it later)

### Set Bot Permissions
- [ ] Scroll to "Privileged Gateway Intents"
- [ ] Enable "SERVER MEMBERS INTENT"
- [ ] Enable "MESSAGE CONTENT INTENT"
- [ ] Save changes

### Generate Invite URL
- [ ] Go to "OAuth2" → "URL Generator"
- [ ] Select scopes:
  - [ ] `bot`
  - [ ] `applications.commands`
- [ ] Select permissions:
  - [ ] Send Messages
  - [ ] Embed Links
  - [ ] Read Message History
  - [ ] Use Slash Commands
- [ ] Copy generated URL

### Invite Bot to Server
- [ ] Open the invite URL in browser
- [ ] Select your Discord server
- [ ] Click "Authorize"
- [ ] Complete captcha if prompted
- [ ] Verify bot appears in server member list

### Get Discord IDs
- [ ] Enable Developer Mode (Settings → Advanced → Developer Mode)
- [ ] Right-click your server icon → Copy Server ID → Save it
- [ ] Right-click your signals channel → Copy Channel ID → Save it

---

## Phase 3: Binance API Setup 🔑

### Option A: Testnet (Recommended for Testing)

- [ ] Go to https://testnet.binancefuture.com
- [ ] Click "Login with GitHub"
- [ ] Authorize the application
- [ ] Click on your email in top-right → "API Key"
- [ ] Generate new API key
- [ ] Copy API Key
- [ ] Copy Secret Key
- [ ] Save both securely

### Option B: Mainnet (Live Trading)

⚠️ **Warning: Real money at risk!**

- [ ] Go to https://www.binance.com
- [ ] Login to your account
- [ ] Complete verification (if not done)
- [ ] Enable 2FA (Security → Two-Factor Authentication)
- [ ] Go to Profile → API Management
- [ ] Create API Key
- [ ] Complete verification (email, 2FA)
- [ ] Save API Key
- [ ] Save Secret Key
- [ ] Click "Edit Restrictions"
- [ ] Set IP access restriction (optional but recommended)
- [ ] Enable permissions:
  - [ ] Enable Reading
  - [ ] Enable Futures
  - [ ] **DO NOT** enable Withdrawals
- [ ] Save changes

---

## Phase 4: Bot Installation 💻

### Download Project
- [ ] Navigate to project folder: `cd i:\Discord_Bot\athena_bot`
- [ ] Verify all files are present (see file list below)

### Required Files Check
- [ ] bot.py
- [ ] binance_client.py
- [ ] signal_analyzer.py
- [ ] strategies.py
- [ ] config.py
- [ ] logger.py
- [ ] requirements.txt
- [ ] .env.example
- [ ] README.md
- [ ] setup.ps1

### Run Setup Script
- [ ] Open PowerShell in project folder
- [ ] Run: `.\setup.ps1`
- [ ] Wait for completion
- [ ] Verify no errors

### Manual Setup (if script fails)
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate it: `.\venv\Scripts\Activate.ps1`
- [ ] Install packages: `pip install -r requirements.txt`
- [ ] Create directories: `logs/` and `trading_data/`
- [ ] Copy `.env.example` to `.env`

---

## Phase 5: Configuration ⚙️

### Create .env File
- [ ] Copy `.env.example` to `.env`
- [ ] Open `.env` in text editor

### Fill in Discord Configuration
```env
DISCORD_BOT_TOKEN=paste_your_discord_token_here
DISCORD_GUILD_ID=paste_your_server_id_here
SIGNAL_CHANNEL_ID=paste_your_channel_id_here
```

- [ ] Paste Discord bot token
- [ ] Paste server (guild) ID
- [ ] Paste channel ID for signals

### Fill in Binance Configuration
```env
BINANCE_API_KEY=paste_your_binance_key_here
BINANCE_API_SECRET=paste_your_binance_secret_here
BINANCE_TESTNET=True  # or False for mainnet
```

- [ ] Paste Binance API key
- [ ] Paste Binance API secret
- [ ] Set testnet to True (recommended) or False

### Configure Trading Settings
```env
DEFAULT_LEVERAGE=5
DEFAULT_ORDER_SIZE_USDT=50
DEFAULT_RISK_PERCENTAGE=1.0
MAX_POSITIONS=2
TRADING_ENABLED=False
LOG_LEVEL=INFO
```

- [ ] Set leverage (start low: 3-5x)
- [ ] Set order size (start small: $50-100)
- [ ] Set risk percentage (1-2% recommended)
- [ ] Set max positions (2-3 to start)
- [ ] Leave trading disabled initially
- [ ] Set log level (INFO for normal, DEBUG for troubleshooting)

### Save Configuration
- [ ] Save `.env` file
- [ ] Verify no syntax errors
- [ ] Double-check all keys are correct

---

## Phase 6: Testing 🧪

### Run System Check
- [ ] Open PowerShell in project folder
- [ ] Run: `python test_setup.py`
- [ ] Review output
- [ ] Verify all checks pass ✅

### Fix Any Issues
If any checks fail:

**Python Version:**
- [ ] Install Python 3.9+ from python.org
- [ ] Restart terminal

**Missing Packages:**
- [ ] Run: `pip install -r requirements.txt`
- [ ] Check for errors
- [ ] Retry

**Configuration Issues:**
- [ ] Review `.env` file
- [ ] Check for typos
- [ ] Verify API keys are correct

**Binance Connection:**
- [ ] Verify API keys
- [ ] Check internet connection
- [ ] Try testnet if mainnet fails

---

## Phase 7: First Run 🚀

### Start the Bot
- [ ] Run: `python bot.py`
- [ ] Wait for startup messages
- [ ] Look for "Bot logged in as..." message
- [ ] Verify "Connected to Binance" message
- [ ] Check for any error messages

### Verify Bot is Online
- [ ] Open Discord
- [ ] Check bot appears online (green status)
- [ ] Bot should be in server member list

### Test Commands
In Discord, test each command:

- [ ] `/help` - Should show help message
- [ ] `/strategies` - Should list strategies
- [ ] `/price symbol:BTCUSDT` - Should show BTC price
- [ ] `/signal symbol:BTCUSDT` - Should generate signal
- [ ] `/balance` - Should show your balance
- [ ] `/positions` - Should show positions (or "none")

### Expected Results
Each command should:
- [ ] Respond within 5 seconds
- [ ] Show formatted embed message
- [ ] Display relevant information
- [ ] No error messages

---

## Phase 8: Advanced Testing 🎯

### Test Different Strategies
- [ ] `/signal symbol:ETHUSDT strategy:EMA_CROSS`
- [ ] `/signal symbol:BTCUSDT strategy:MACD_SIGNAL`
- [ ] `/signal symbol:SOLUSDT strategy:RSI_DIVERGENCE`
- [ ] `/signal symbol:BNBUSDT strategy:TRIPLE_EMA`

### Test Market Scanning
- [ ] `/scan strategy:EMA_CROSS interval:15m min_strength:50`
- [ ] `/scan strategy:MACD_SIGNAL interval:1h min_strength:60`
- [ ] Verify results show multiple symbols
- [ ] Check signals are ranked by strength

### Test Monitoring
- [ ] `/monitor action:start channel:#your-channel`
- [ ] Wait 15 minutes
- [ ] Check if signals appear in channel
- [ ] `/monitor action:stop`
- [ ] Verify monitoring stopped

---

## Phase 9: Optimization ⚡

### Fine-tune Settings

Based on testing, adjust in `.env`:

**If too many signals:**
```env
# Increase thresholds in config.py
RSI_OVERSOLD = 25  # More extreme
```

**If too few signals:**
```env
# Decrease thresholds in config.py
RSI_OVERSOLD = 35  # Less extreme
```

**Performance tuning:**
- [ ] Adjust `min_signal_strength` in scan commands
- [ ] Change monitoring interval in bot.py
- [ ] Modify tracked symbols list
- [ ] Test different strategies

---

## Phase 10: Going Live 💰

### Before Live Trading

⚠️ **Only proceed if:**
- [ ] Tested thoroughly on testnet for 1-2 weeks
- [ ] Understand all strategies
- [ ] Comfortable with risk management
- [ ] Have trading plan
- [ ] Starting with money you can afford to lose

### Switch to Mainnet

In `.env`:
```env
BINANCE_TESTNET=False
```

- [ ] Change testnet to False
- [ ] Use mainnet API keys
- [ ] Restart bot
- [ ] Test with very small amounts first

### Enable Trading (Optional)

In `.env`:
```env
TRADING_ENABLED=True
```

⚠️ **Warning:** This allows bot to execute trades automatically!

- [ ] Understand this enables real trading
- [ ] Set position size very small
- [ ] Monitor closely
- [ ] Have stop loss strategy

### Start Small
- [ ] Begin with $50-100 positions
- [ ] Use 3-5x leverage maximum
- [ ] Trade 1-2 positions max
- [ ] Monitor every trade
- [ ] Keep detailed journal

---

## Phase 11: Monitoring & Maintenance 📊

### Daily Tasks
- [ ] Check bot is running
- [ ] Review overnight signals
- [ ] Check account balance
- [ ] Review open positions
- [ ] Check logs for errors

### Weekly Tasks
- [ ] Review trading performance
- [ ] Adjust strategies if needed
- [ ] Update tracked symbols
- [ ] Backup configuration
- [ ] Check API key usage

### Monthly Tasks
- [ ] Review overall profitability
- [ ] Compare strategies
- [ ] Adjust risk parameters
- [ ] Rotate API keys
- [ ] Update dependencies

---

## Phase 12: Troubleshooting 🔧

### Common Issues

**Bot won't start:**
- [ ] Check Python version
- [ ] Verify all packages installed
- [ ] Check .env file exists
- [ ] Review error messages

**Commands not working:**
- [ ] Verify bot is online
- [ ] Check permissions
- [ ] Try `/help` command
- [ ] Restart bot

**No signals appearing:**
- [ ] Check symbol is valid
- [ ] Try different strategy
- [ ] Lower min_strength
- [ ] Check market conditions

**Binance errors:**
- [ ] Verify API keys
- [ ] Check API permissions
- [ ] Try testnet
- [ ] Check account restrictions

**Monitoring not working:**
- [ ] Verify channel ID correct
- [ ] Check bot has send permissions
- [ ] Review monitoring status
- [ ] Check bot logs

---

## Emergency Procedures 🚨

### If Something Goes Wrong

**Stop the bot immediately:**
```powershell
# Press Ctrl+C in terminal
```

**Close all positions manually:**
- [ ] Login to Binance
- [ ] Go to Futures
- [ ] Close all positions
- [ ] Cancel all orders

**Disable API key:**
- [ ] Binance → API Management
- [ ] Disable or delete API key
- [ ] Investigate issue
- [ ] Create new key when resolved

---

## Success Metrics 📈

### You're ready when:

- [ ] Bot runs 24/7 without issues
- [ ] All commands respond correctly
- [ ] Signals generate accurately
- [ ] You understand each strategy
- [ ] Risk management is working
- [ ] Logging is functioning
- [ ] You have a trading plan
- [ ] Comfortable with the system

---

## Resources 📚

### Documentation
- [ ] Read full README.md
- [ ] Study QUICKSTART.md
- [ ] Review CONFIGURATION.md
- [ ] Check PROJECT_SUMMARY.md

### External Resources
- [ ] Binance API Docs
- [ ] Discord.py Documentation
- [ ] Technical Analysis tutorials
- [ ] Risk management guides

---

## Final Checklist ✨

- [ ] Bot is running smoothly
- [ ] All commands tested
- [ ] Testnet trading successful
- [ ] Configuration optimized
- [ ] Documentation read
- [ ] Emergency procedures known
- [ ] Risk management in place
- [ ] Trading plan created
- [ ] Journal started
- [ ] Ready to trade responsibly!

---

**🎉 Congratulations! You're all set up!**

Remember:
- Start small
- Use stop losses
- Trade responsibly
- Keep learning
- Never risk more than you can afford to lose

**Good luck with your trading journey! 🚀**
