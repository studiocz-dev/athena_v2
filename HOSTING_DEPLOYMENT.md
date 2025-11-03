# 🚀 Athena Bot v2.0 - Hosting Deployment Guide

**Repository**: https://github.com/studiocz-dev/athena_v2  
**Commit**: 0490348 (Latest)  
**Status**: ✅ Production Ready  
**Bot Running Locally**: FutureBot#6502 (since 06:19:54)

---

## 🎯 Deployment Options

### Option 1: BotGhost.net (Recommended for Discord Bots)

**Not Tested Yet** - BotGhost.net is typically for Discord.js bots. For Python bots, consider alternatives below.

### Option 2: Railway.app ⭐ **HIGHLY RECOMMENDED**

**Best for Python Discord bots** - Free tier available, easy setup.

**Steps:**

1. **Sign up at Railway.app**:
   - Visit https://railway.app
   - Sign in with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `studiocz-dev/athena_v2`
   - Branch: `main`

3. **Configure Environment Variables**:
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   SIGNAL_CHANNEL_ID=your_channel_id_here
   EXCHANGE=binance
   BINANCE_API_KEY=your_binance_api_key_here
   BINANCE_API_SECRET=your_binance_api_secret_here
   BINANCE_TESTNET=True
   TRADING_ENABLED=False
   ```
   
   **📝 Note**: Get your actual values from `.env` file on your local machine

4. **Configure Start Command**:
   - In Railway dashboard → Settings → Deploy
   - Start Command: `python src/athena_launcher.py`

5. **Deploy**:
   - Railway auto-deploys from GitHub
   - Monitor logs in dashboard
   - Bot will appear online in Discord

**Cost**: Free tier (500 hours/month) - enough for 24/7

---

### Option 3: Render.com ⭐ **EXCELLENT ALTERNATIVE**

**Similar to Railway, also free tier available**

**Steps:**

1. **Sign up at Render.com**:
   - Visit https://render.com
   - Sign in with GitHub

2. **Create New Web Service**:
   - Click "New +"
   - Select "Background Worker" (not Web Service)
   - Connect GitHub repo: `studiocz-dev/athena_v2`

3. **Configure**:
   - **Name**: athena-trading-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/athena_launcher.py`

4. **Add Environment Variables**:
   (Same as Railway.app list above)

5. **Deploy**:
   - Click "Create Background Worker"
   - Monitor logs
   - Bot will come online

**Cost**: Free tier available

---

### Option 4: PythonAnywhere.com

**Best for simple Python hosting**

**Steps:**

1. **Sign up**: https://www.pythonanywhere.com
2. **Upload code via Git**:
   ```bash
   git clone https://github.com/studiocz-dev/athena_v2.git
   cd athena_v2
   pip3.10 install --user -r requirements.txt
   ```

3. **Create .env file**:
   ```bash
   nano .env
   # Paste environment variables
   ```

4. **Run bot**:
   - Dashboard → Tasks → Add scheduled task
   - Command: `python3.10 /home/yourusername/athena_v2/src/athena_launcher.py`
   - Or use "Always-on task" (paid plan)

**Cost**: Free tier limited, $5/month for always-on

---

### Option 5: DigitalOcean Droplet

**Best for full control and scalability**

**Steps:**

1. **Create Droplet**:
   - OS: Ubuntu 22.04 LTS
   - Plan: Basic ($4-6/month)
   - Datacenter: Closest to you

2. **SSH into server**:
   ```bash
   ssh root@your_droplet_ip
   ```

3. **Install dependencies**:
   ```bash
   apt update
   apt install python3.10 python3-pip git -y
   ```

4. **Clone and setup**:
   ```bash
   git clone https://github.com/studiocz-dev/athena_v2.git
   cd athena_v2
   pip3 install -r requirements.txt
   ```

5. **Configure environment**:
   ```bash
   nano .env
   # Paste environment variables (Ctrl+X to save)
   ```

6. **Run with systemd** (auto-restart):
   ```bash
   nano /etc/systemd/system/athena-bot.service
   ```
   
   Paste:
   ```ini
   [Unit]
   Description=Athena Trading Bot
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/athena_v2
   ExecStart=/usr/bin/python3 /root/athena_v2/src/athena_launcher.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   systemctl daemon-reload
   systemctl enable athena-bot
   systemctl start athena-bot
   systemctl status athena-bot
   ```

7. **Monitor logs**:
   ```bash
   journalctl -u athena-bot -f
   ```

**Cost**: $4-6/month

---

### Option 6: Heroku

**Popular but less friendly for Python bots now**

**Steps:**

1. **Install Heroku CLI**: https://devcenter.heroku.com/articles/heroku-cli

2. **Login and create app**:
   ```bash
   heroku login
   heroku create athena-trading-bot
   ```

3. **Set environment variables** (use your actual values from `.env`):
   ```bash
   heroku config:set DISCORD_BOT_TOKEN="your_token_here"
   heroku config:set SIGNAL_CHANNEL_ID="your_channel_id"
   heroku config:set EXCHANGE="binance"
   heroku config:set BINANCE_API_KEY="your_key_here"
   heroku config:set BINANCE_API_SECRET="your_secret_here"
   heroku config:set BINANCE_TESTNET="True"
   heroku config:set TRADING_ENABLED="False"
   ```

4. **Create Procfile**:
   ```bash
   echo "worker: python src/athena_launcher.py" > Procfile
   git add Procfile
   git commit -m "Add Procfile"
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   heroku ps:scale worker=1
   heroku logs --tail
   ```

**Cost**: Free tier removed, starts at $5/month

---

## 🔍 Post-Deployment Checklist

### 1. Verify Bot is Online

**Discord:**
- Check bot appears online (green dot)
- Run command: `!status`
- Expected response: Bot stats and balance

### 2. Monitor First Scan

**Wait 15 minutes for first market analysis:**
- Check Discord channel (1423658108286275717)
- Should see bot activity logs (if any signals)
- No signals is normal if market conditions weak

### 3. Check Logs

**Common log messages:**
```
✅ Bot logged in as FutureBot#6502
🔍 Market Scan Started
📊 Analyzing BTCUSDT...
⏸️ BTCUSDT: HOLD - no signal (normal)
```

**Good signal example:**
```
🚀 BUY SIGNAL - ETHUSDT
⭐⭐⭐⭐ (4/5 Stars)
💰 Entry: $4,250.00
```

### 4. Performance Expectations

- **First 24 Hours**: 5-15 signals total
- **Signal Quality**: 50%+ confidence, 2+ stars minimum
- **Trading**: DISABLED (signal-only mode)
- **Uptime**: Should stay online 24/7

---

## 🛠️ Troubleshooting

### Bot Not Coming Online

**Check:**
1. Discord token is correct
2. Bot has proper permissions in server
3. Python version is 3.10+
4. All dependencies installed

**Fix:**
```bash
# Test locally first
python scripts/test_complete_system.py
```

### No Signals Received

**This is NORMAL if:**
- Market is ranging (no strong trends)
- All strategies in disagreement
- ATR below 1.25% threshold

**Force a test:**
- Current market conditions may simply not meet criteria
- Wait for volatile market movements
- Bot analyzes every 15 minutes automatically

### API Errors

**Binance 401 Unauthorized:**
- Verify API keys are correct
- Check BINANCE_TESTNET=True (for testnet keys)
- Ensure keys have Futures permissions

**Connection timeout:**
- Check internet connection
- Binance may be rate limiting (unlikely with 15-min interval)

### Bot Crashes/Restarts

**Check logs for:**
- Memory issues (upgrade hosting plan)
- API rate limits (should not happen with current setup)
- Discord connection drops (usually auto-reconnects)

---

## 📊 Monitoring Dashboard

### Required Checks

**Daily:**
- ✅ Bot online status
- ✅ Signal quality (star ratings)
- ✅ Any error messages in logs

**Weekly:**
- ✅ Signal frequency (should be 35-100/week)
- ✅ Strategy distribution (all 8 working)
- ✅ Balance unchanged (signal-only mode)

**Monthly:**
- ✅ Update dependencies
- ✅ Review strategy performance
- ✅ Consider parameter tuning

---

## 🔐 Security Best Practices

### DO:
- ✅ Use testnet for initial deployment
- ✅ Keep TRADING_ENABLED=False until confident
- ✅ Monitor logs daily
- ✅ Keep API keys in environment variables (not code)
- ✅ Use read-only API keys if possible

### DON'T:
- ❌ Share your .env file
- ❌ Commit API keys to GitHub
- ❌ Enable trading without testing
- ❌ Use live exchange keys on testnet
- ❌ Ignore error messages

---

## 🎉 Success Metrics

### Week 1: Testing Phase
- ✅ Bot stays online 24/7
- ✅ Receives 35-100 signals
- ✅ No crashes or errors
- ✅ All strategies functioning

### Week 2-4: Validation Phase
- ✅ Signal quality consistent
- ✅ Confidence scores reasonable
- ✅ Win rate tracking (if paper trading)
- ✅ Consider live trading (with caution)

---

## 📞 Support Resources

**GitHub Issues**: https://github.com/studiocz-dev/athena_v2/issues  
**Discord Bot**: `!status` command  
**Logs**: Check hosting platform dashboard

---

## 🚀 Quick Deploy Commands

### For Railway.app / Render.com:
1. Connect GitHub repo
2. Add environment variables
3. Set start command: `python src/athena_launcher.py`
4. Deploy

### For VPS (Ubuntu):
```bash
# One-line setup
git clone https://github.com/studiocz-dev/athena_v2.git && cd athena_v2 && pip3 install -r requirements.txt && nano .env

# Run bot
python3 src/athena_launcher.py

# Or with nohup (background)
nohup python3 src/athena_launcher.py > bot.log 2>&1 &

# Check logs
tail -f bot.log
```

---

## ✅ Deployment Complete!

**Your bot is now:**
- ✅ Committed to GitHub (commit: 0490348)
- ✅ Ready for hosting deployment
- ✅ Fully tested and operational
- ✅ Running locally as FutureBot#6502
- ✅ Signal-only mode (safe)

**Next steps:**
1. Choose hosting platform (Railway.app recommended)
2. Deploy using guide above
3. Monitor Discord for signals
4. Enjoy automated trading signals! 🎉

---

**Built with ❤️ | Version 2.0.0 | Production Ready**
