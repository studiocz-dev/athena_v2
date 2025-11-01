# 🤖 Athena - Binance Futures Trading Signal Discord Bot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Discord.py](https://img.shields.io/badge/Discord.py-2.3.2-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

**A fully functional Discord bot for Binance Futures trading signals with multiple technical analysis strategies**

[Features](#-features) • [Installation](#-installation) • [Configuration](#-configuration) • [Commands](#-commands) • [Strategies](#-trading-strategies) • [Screenshots](#-screenshots)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Discord Bot Setup](#-discord-bot-setup)
- [Binance API Setup](#-binance-api-setup)
- [Usage](#-usage)
- [Commands](#-commands)
- [Trading Strategies](#-trading-strategies)
- [Risk Management](#-risk-management)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#-disclaimer)
- [License](#-license)

---

## ✨ Features

### 🎯 Core Features
- **Real-time Signal Generation**: Analyze Binance Futures markets with 7+ technical strategies
- **Discord Integration**: Modern slash commands with beautiful embeds
- **14-Symbol Watchlist**: Expanded coverage across majors, large-caps, and L2 coins
- **ATR Volatility Filter**: Smart filtering to skip ranging markets and focus on trending opportunities
- **Multi-Timeframe Analysis**: MTF confirmation across 15m, 1h, and 4h timeframes
- **Automatic Monitoring**: Background task to send signals to designated channel
- **Account Management**: Check balance, positions, and P&L directly from Discord
- **Risk Management**: Automatic stop-loss and take-profit calculations
- **Multiple Strategies**: EMA Cross, MACD, RSI, Stochastic RSI, Breakouts, and more

### 📊 Trading Strategies
1. **EMA Crossover** - Fast and slow EMA crossover signals
2. **Triple EMA** - Three EMA alignment for trend confirmation
3. **RSI Divergence** - RSI extremes and divergence detection
4. **MACD Signal** - MACD and signal line crossovers
5. **Stochastic RSI** - StochRSI overbought/oversold signals
6. **Breakout** - Volume-confirmed price breakouts
7. **Support/Resistance** - Bounce plays off key levels

### 🛡️ Safety Features
- Configurable leverage (1x-125x)
- Automatic position sizing
- Risk/reward ratio calculations
- Testnet support for paper trading
- Position limits and risk controls

---

## 📦 Requirements

- Python 3.9 or higher
- Discord Bot Token
- Binance Futures API Key & Secret
- Windows/Linux/MacOS

---

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd athena_bot
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Edit `.env` File

Open `.env` and configure the following:

```env
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
SIGNAL_CHANNEL_ID=your_signal_channel_id_here

# Binance API Configuration
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
BINANCE_TESTNET=False  # Set to True for testnet

# Trading Configuration
DEFAULT_LEVERAGE=10
DEFAULT_ORDER_SIZE_USDT=100
DEFAULT_RISK_PERCENTAGE=1.0
MAX_POSITIONS=3

# Bot Settings
TRADING_ENABLED=False  # Set to True to enable trading
LOG_LEVEL=INFO
```

---

## 🤖 Discord Bot Setup

### 1. Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**
3. Name your application (e.g., "Athena Trading Bot")
4. Go to **"Bot"** section
5. Click **"Add Bot"**
6. **Copy the Bot Token** and paste it into `.env` as `DISCORD_BOT_TOKEN`

### 2. Configure Bot Permissions

In the **Bot** section:
- Enable **MESSAGE CONTENT INTENT**
- Enable **SERVER MEMBERS INTENT**

### 3. Invite Bot to Your Server

1. Go to **OAuth2 > URL Generator**
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - `Send Messages`
   - `Embed Links`
   - `Read Message History`
   - `Use Slash Commands`
4. Copy the generated URL and open in browser
5. Select your server and authorize

### 4. Get Guild ID and Channel ID

**Enable Developer Mode in Discord:**
- Settings → Advanced → Developer Mode

**Get Guild ID:**
- Right-click your server icon → Copy Server ID

**Get Channel ID:**
- Right-click the channel you want signals in → Copy Channel ID

Paste these into your `.env` file.

---

## 🔑 Binance API Setup

### 1. Create Binance Account

- Sign up at [Binance](https://www.binance.com)
- Enable **Two-Factor Authentication** (2FA)
- Complete verification (for higher limits)

### 2. Create API Keys

1. Go to **Profile** → **API Management**
2. Create a new API key
3. Name it (e.g., "Athena Trading Bot")
4. **Save the API Key and Secret** securely
5. Enable permissions:
   - ✅ **Enable Reading**
   - ✅ **Enable Futures**
   - ❌ **Disable Withdrawals** (for safety)

### 3. Configure API Restrictions (Optional but Recommended)

- Restrict Access to Trusted IPs
- Set daily withdrawal limit to 0

### 4. Test with Testnet First

For testing without real money:

1. Go to [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Login with GitHub
3. Get testnet API keys
4. Set `BINANCE_TESTNET=True` in `.env`

---

## 📖 Usage

### Starting the Bot

```bash
python bot.py
```

You should see:
```
2024-01-01 12:00:00 - AthenaBot - INFO - Setting up Athena Bot...
2024-01-01 12:00:00 - BinanceClient - INFO - Connected to Binance Futures MAINNET
2024-01-01 12:00:00 - AthenaBot - INFO - Synced 8 command(s)
2024-01-01 12:00:00 - AthenaBot - INFO - Bot logged in as AthenaBot#1234
```

---

## 💬 Commands

### Basic Commands

#### `/signal` - Get Trading Signal
Generate a trading signal for a specific symbol.

```
/signal symbol:BTCUSDT strategy:EMA_CROSS interval:15m
```

**Parameters:**
- `symbol`: Trading pair (e.g., BTCUSDT, ETHUSDT)
- `strategy`: Strategy name (default: EMA_CROSS)
- `interval`: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)

#### `/scan` - Scan Multiple Symbols
Scan top symbols for trading opportunities.

```
/scan strategy:MACD_SIGNAL interval:1h min_strength:60
```

**Parameters:**
- `strategy`: Strategy to use
- `interval`: Timeframe
- `min_strength`: Minimum signal strength (0-100)

#### `/price` - Get Current Price
Check current market price for a symbol.

```
/price symbol:BTCUSDT
```

### Account Commands

#### `/balance` - Check Balance
View your Binance Futures account balance.

```
/balance
```

#### `/positions` - View Positions
See all your open positions with P&L.

```
/positions
```

### Monitoring Commands

#### `/monitor` - Toggle Auto Monitoring
Start or stop automatic signal monitoring.

```
/monitor action:start channel:#trading-signals
/monitor action:stop
```

When active, the bot will:
- Scan symbols every 15 minutes
- Post top signals to the specified channel
- Use configurable strategy and filters

### Information Commands

#### `/strategies` - List Strategies
View all available trading strategies.

```
/strategies
```

#### `/help` - Show Help
Display all available commands.

```
/help
```

---

## 📊 Trading Strategies

### 1. EMA Crossover (EMA_CROSS)
**Best for:** Trend following

**How it works:**
- Fast EMA (9) crosses above/below Slow EMA (21)
- **Long:** Fast EMA crosses above Slow EMA
- **Short:** Fast EMA crosses below Slow EMA

**Timeframes:** 15m, 1h, 4h

---

### 2. Triple EMA (TRIPLE_EMA)
**Best for:** Strong trend confirmation

**How it works:**
- Uses 3 EMAs: 9, 21, 50
- **Long:** All EMAs aligned (9 > 21 > 50) + Fast crosses Medium
- **Short:** All EMAs aligned (9 < 21 < 50) + Fast crosses Medium

**Timeframes:** 1h, 4h, 1d

---

### 3. RSI Divergence (RSI_DIVERGENCE)
**Best for:** Reversal trading

**How it works:**
- RSI below 30 = Oversold (Long signal)
- RSI above 70 = Overbought (Short signal)
- Detects price/RSI divergences

**Timeframes:** 15m, 1h, 4h

---

### 4. MACD Signal (MACD_SIGNAL)
**Best for:** Momentum trading

**How it works:**
- MACD line crosses Signal line
- **Long:** MACD crosses above Signal
- **Short:** MACD crosses below Signal
- Histogram used for strength

**Timeframes:** 1h, 4h

---

### 5. Stochastic RSI (STOCH_RSI)
**Best for:** Overbought/Oversold

**How it works:**
- StochRSI K and D lines
- **Long:** K crosses D in oversold zone (<20)
- **Short:** K crosses D in overbought zone (>80)

**Timeframes:** 15m, 1h

---

### 6. Breakout (BREAKOUT)
**Best for:** Volatility expansion

**How it works:**
- Identifies 20-period high/low
- Requires volume confirmation (>1.5x average)
- **Long:** Price breaks above resistance
- **Short:** Price breaks below support

**Timeframes:** 15m, 1h, 4h

---

### 7. Support/Resistance (SUPPORT_RESISTANCE)
**Best for:** Bounce plays

**How it works:**
- Finds key support/resistance levels
- **Long:** Price bounces off support
- **Short:** Price rejects at resistance
- Works best in ranging markets

**Timeframes:** 1h, 4h

---

## 🛡️ Risk Management

### Default Settings

```python
DEFAULT_LEVERAGE = 10x
DEFAULT_ORDER_SIZE = $100 USDT
DEFAULT_STOP_LOSS = 2% of entry
DEFAULT_TAKE_PROFIT = 4% of entry (2:1 R/R)
MAX_POSITIONS = 3
```

### Position Sizing Example

With $1000 account:
- **Order Size:** $100 USDT
- **Leverage:** 10x
- **Position Size:** $1000 worth of contracts
- **Risk per trade:** $20 (2% SL)
- **Reward potential:** $40 (4% TP)

### Best Practices

1. **Never risk more than 1-2% per trade**
2. **Use stop-losses on every trade**
3. **Start with lower leverage (5-10x)**
4. **Test strategies on testnet first**
5. **Keep a trading journal**
6. **Don't overtrade - quality over quantity**
7. **Never trade more than you can afford to lose**

---

## 📁 Project Structure

```
athena_bot/
│
├── bot.py                  # Main Discord bot
├── binance_client.py       # Binance API wrapper
├── signal_analyzer.py      # Signal generation
├── strategies.py           # Trading strategies
├── config.py               # Configuration management
├── logger.py               # Logging setup
│
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment file
├── .env                   # Your environment file (create this)
├── .gitignore            # Git ignore file
├── README.md             # This file
│
├── logs/                 # Log files (auto-created)
│   └── athena_bot.log
│
├── trading_data/         # Database files (auto-created)
│   └── athena_bot.db
│
└── repos/                # Reference repositories
    ├── Binance-Futures-Trading-Bot-main/
    ├── freqtrade-develop/
    └── ...
```

---

## 🔧 Troubleshooting

### Bot doesn't respond to commands

**Solution:**
1. Check bot has proper permissions in Discord
2. Verify bot is online (green status)
3. Try re-syncing commands: restart the bot
4. Enable MESSAGE CONTENT INTENT in Discord Developer Portal

### "Failed to initialize Binance client"

**Solution:**
1. Check API keys are correct in `.env`
2. Verify API has Futures permission enabled
3. Check internet connection
4. If using IP restriction, add your IP to whitelist

### "No signal found"

**Solution:**
- Market conditions may not meet strategy criteria
- Try different strategy or timeframe
- Lower `min_strength` parameter in `/scan`
- Check if symbol is active and trading

### Import errors

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### "Timestamp for this request is outside of the recvWindow"

**Solution:**
- Sync your system time
- Windows: Run `w32tm /resync` in admin PowerShell
- Linux: Run `sudo ntpdate -s time.nist.gov`

---

## ⚠️ Disclaimer

**IMPORTANT: Please read carefully**

- This bot is for **EDUCATIONAL PURPOSES ONLY**
- Trading cryptocurrencies involves **SIGNIFICANT RISK**
- You can **LOSE ALL YOUR MONEY**
- Past performance does **NOT guarantee future results**
- The developers are **NOT responsible** for any losses
- **Always test on testnet first**
- **Never invest more than you can afford to lose**
- **Not financial advice** - do your own research (DYOR)

By using this bot, you acknowledge that:
1. You understand the risks of trading
2. You are responsible for your own trading decisions
3. You will not hold the developers liable for any losses
4. You have tested thoroughly on testnet before live trading

---

## 📜 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📞 Support

- **Issues:** Open an issue on GitHub
- **Discord:** Join our Discord server (link)
- **Documentation:** Read this README carefully

---

## 🙏 Acknowledgments

This project was built using knowledge from:
- Binance Futures Trading Bot repositories
- Freqtrade algorithmic trading framework
- Technical analysis libraries (ta-lib, pandas)
- Discord.py community

---

## 📈 Roadmap

- [ ] Web dashboard for monitoring
- [ ] Backtesting framework
- [ ] More advanced strategies
- [ ] Portfolio management
- [ ] Trade execution from Discord
- [ ] Multi-exchange support
- [ ] Machine learning signals

---

<div align="center">

**Made with ❤️ for the crypto trading community**

⭐ Star this repo if you find it useful!

</div>
