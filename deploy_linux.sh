#!/bin/bash
# Athena Bot - Linux/VPS Deployment Script

echo "=================================================="
echo "🚀 ATHENA BOT - SERVER DEPLOYMENT"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root or with sudo"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Python 3.10+
echo "🐍 Installing Python 3.10..."
apt-get install -y python3.10 python3.10-venv python3-pip

# Install system dependencies for TA-Lib
echo "📊 Installing TA-Lib dependencies..."
apt-get install -y build-essential wget
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
make install
cd ~

# Create deployment directory
echo "📁 Creating deployment directory..."
mkdir -p /opt/athena_bot
cd /opt/athena_bot

# Clone or copy bot files (modify this based on your setup)
echo "📥 Setting up bot files..."
# If using git:
# git clone https://github.com/yourusername/athena_bot.git .
# Or if uploading directly, files should already be here

# Create Python virtual environment
echo "🔧 Creating virtual environment..."
python3.10 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_token_here
DISCORD_GUILD_ID=your_guild_id
SIGNAL_CHANNEL_ID=your_channel_id

# Exchange Selection (gate, bybit, or binance)
EXCHANGE=binance

# Gate.io API Configuration (TESTNET)
GATE_API_KEY=your_gate_api_key
GATE_API_SECRET=your_gate_api_secret
GATE_TESTNET=True

# Bybit API Configuration
BYBIT_API_KEY=your_bybit_key
BYBIT_API_SECRET=your_bybit_secret
BYBIT_DEMO=True

# Binance API Configuration
BINANCE_API_KEY=your_binance_key
BINANCE_API_SECRET=your_binance_secret
BINANCE_TESTNET=True

# Trading Configuration
DEFAULT_LEVERAGE=10
DEFAULT_ORDER_SIZE_USDT=100
DEFAULT_RISK_PERCENTAGE=1.0
MAX_POSITIONS=3

# Bot Settings
TRADING_ENABLED=False
LOG_LEVEL=INFO
EOF
    echo "⚠️  Please edit /opt/athena_bot/.env with your API keys!"
fi

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/athena-bot.service << 'EOF'
[Unit]
Description=Athena Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/athena_bot
Environment="PATH=/opt/athena_bot/venv/bin"
ExecStart=/opt/athena_bot/venv/bin/python /opt/athena_bot/src/athena_launcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
echo "📝 Creating log directory..."
mkdir -p /var/log/athena_bot

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

echo ""
echo "=================================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo "1. Edit configuration:"
echo "   nano /opt/athena_bot/.env"
echo ""
echo "2. Start the bot:"
echo "   systemctl start athena-bot"
echo ""
echo "3. Enable auto-start on boot:"
echo "   systemctl enable athena-bot"
echo ""
echo "4. Check bot status:"
echo "   systemctl status athena-bot"
echo ""
echo "5. View logs:"
echo "   journalctl -u athena-bot -f"
echo ""
echo "=================================================="
