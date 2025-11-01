# 📁 Project Structure

```
athena_bot/
├── src/                           # 🎯 Core source code
│   ├── __init__.py               
│   ├── auto_trader.py            # Main automated trading bot
│   ├── bot.py                    # Simple Discord bot
│   ├── binance_client.py         # Binance API wrapper
│   ├── config.py                 # Configuration loader
│   ├── logger.py                 # Logging utilities
│   ├── mtf_analyzer.py           # Multi-timeframe analyzer
│   ├── signal_analyzer.py        # Basic signal analyzer
│   ├── signal_analyzer_enhanced.py  # Enhanced MTF signal analyzer
│   ├── strategies.py             # Base trading strategies
│   └── strategies_enhanced.py    # Optimized strategies with ATR

├── scripts/                       # 🛠️ Utility scripts
│   ├── backtest.py               # Single symbol backtesting
│   ├── batch_backtest.py         # Multi-symbol backtesting
│   ├── advanced_backtest.py      # MTF backtest with optimization
│   ├── compare_strategies.py     # Strategy comparison tool
│   ├── test_setup.py             # Configuration validator
│   ├── run.ps1                   # Run bot (PowerShell)
│   ├── run_backtest.ps1          # Run backtest (PowerShell)
│   ├── setup.ps1                 # Initial setup script
│   └── deploy_to_bothosting.ps1  # SFTP deployment script

├── docs/                          # 📚 Documentation
│   ├── AUTO_TRADING_GUIDE.md     # Automated trading guide
│   ├── BACKTEST_GUIDE.md         # Backtesting guide
│   ├── BACKTEST_QUICKREF.md      # Backtest quick reference
│   ├── CONFIGURATION.md          # Configuration reference
│   ├── DEPLOYMENT_BOTHOSTING.md  # bot-hosting.net deployment
│   ├── DEPLOYMENT_COMPLETE.md    # Deployment summary
│   ├── DEPLOYMENT_STATUS.md      # Current deployment status
│   ├── GITHUB_ACTIONS_SETUP.md   # GitHub Actions guide
│   ├── MTF_OPTIMIZATION_GUIDE.md # Multi-timeframe guide
│   ├── MTF_QUICKREF.md           # MTF quick reference
│   ├── MTF_SUMMARY.md            # MTF implementation summary
│   ├── PROJECT_SUMMARY.md        # Overall project summary
│   ├── QUICKSTART.md             # Quick start guide
│   ├── SETUP_CHECKLIST.md        # Setup checklist
│   └── WIN_RATE_ANALYSIS.md      # Performance analysis

├── .github/workflows/             # ⚙️ GitHub Actions
│   └── deploy.yml                # Auto-deploy workflow

├── trading_data/                  # 📊 Trading database (auto-created)
│   └── performance.db            # SQLite performance tracking

├── logs/                          # 📝 Log files (auto-created)

├── run_bot.py                     # 🚀 Main launcher script
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (SECRET)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── LICENSE                       # MIT License
└── README.md                     # Main documentation
```

---

## 🚀 Quick Start

### Run the Bot:
```bash
python run_bot.py
```

### Run Backtests:
```bash
python scripts/backtest.py BTCUSDT 30
python scripts/batch_backtest.py
python scripts/compare_strategies.py ETHUSDT 60
```

### Test Configuration:
```bash
python scripts/test_setup.py
```

---

## 📦 What's Deployed to Server

When you push to GitHub, only these files go to bot-hosting.net:

```
/home/container/
├── src/              # All source code
│   └── *.py         # All Python modules
├── run_bot.py       # Launcher
├── requirements.txt # Dependencies
├── .env.example     # Config template
└── LICENSE          # License file
```

**NOT deployed** (stays local):
- ❌ docs/ (documentation - on GitHub only)
- ❌ scripts/ (testing tools - local only)
- ❌ .github/ (CI/CD config)
- ❌ *.md files (documentation)
- ❌ trading_data/ (your database)
- ❌ .env (your secrets)

---

## 🎯 Key Files Explained

### Core Bot (`src/auto_trader.py`)
- **Purpose**: Main automated trading system
- **Features**: MTF analysis, Discord integration, auto-execution, performance tracking
- **Run**: `python run_bot.py`
- **Discord Commands**: `!status`, `!stats`, `!positions`, `!stop`

### Backtesting (`scripts/`)
- **backtest.py**: Test single symbol/strategy
- **batch_backtest.py**: Test multiple symbols
- **advanced_backtest.py**: MTF optimization
- **compare_strategies.py**: Compare baseline/MTF/optimized

### Configuration
- **.env**: Your API keys and tokens (NEVER commit)
- **config.py**: Loads and validates environment variables
- **.env.example**: Template for new setups

---

## 📖 Documentation

All guides are in the `docs/` folder:

- **Quick Start**: `docs/QUICKSTART.md`
- **Full Setup**: `docs/SETUP_CHECKLIST.md`
- **Trading Guide**: `docs/AUTO_TRADING_GUIDE.md`
- **MTF Features**: `docs/MTF_OPTIMIZATION_GUIDE.md`
- **Deployment**: `docs/DEPLOYMENT_BOTHOSTING.md`
- **GitHub Actions**: `docs/GITHUB_ACTIONS_SETUP.md`

---

## 🔧 Development Workflow

### Local Testing:
1. Make changes in `src/`
2. Test locally: `python run_bot.py`
3. Run backtests: `python scripts/backtest.py`

### Deploy to Production:
1. Commit changes: `git add . && git commit -m "Update"`
2. Push to GitHub: `git push origin main`
3. GitHub Actions auto-deploys to bot-hosting.net
4. SSH and restart: `python3 run_bot.py`

---

## ✨ Benefits of This Structure

✅ **Clean separation**: Source code vs scripts vs docs  
✅ **Easy deployment**: Only essential files go to server  
✅ **Professional**: Industry-standard Python project layout  
✅ **Maintainable**: Easy to find and modify files  
✅ **Scalable**: Easy to add new modules/features  

---

See `README.md` for overall project information.
