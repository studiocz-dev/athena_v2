"""
Configuration module for Athena Trading Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID')
SIGNAL_CHANNEL_ID = os.getenv('SIGNAL_CHANNEL_ID')

# Binance Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'False').lower() == 'true'

# Trading Configuration
DEFAULT_LEVERAGE = int(os.getenv('DEFAULT_LEVERAGE', '10'))
DEFAULT_ORDER_SIZE_USDT = float(os.getenv('DEFAULT_ORDER_SIZE_USDT', '100'))
DEFAULT_RISK_PERCENTAGE = float(os.getenv('DEFAULT_RISK_PERCENTAGE', '1.0'))
MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '3'))
TRADING_ENABLED = os.getenv('TRADING_ENABLED', 'False').lower() == 'true'

# Bot Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Trading Intervals (for candle data)
VALID_INTERVALS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d']
DEFAULT_INTERVAL = '15m'

# Trading Strategies
AVAILABLE_STRATEGIES = [
    'EMA_CROSS',
    'RSI_DIVERGENCE',
    'MACD_SIGNAL',
    'STOCH_RSI',
    'TRIPLE_EMA',
    'BREAKOUT',
    'SUPPORT_RESISTANCE'
]

# Risk Management
DEFAULT_STOP_LOSS_PERCENTAGE = 2.0  # 2% stop loss
DEFAULT_TAKE_PROFIT_PERCENTAGE = 4.0  # 4% take profit (2:1 ratio)

# Technical Indicator Periods
EMA_FAST = 9
EMA_SLOW = 21
EMA_TREND = 50
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
STOCH_PERIOD = 14
STOCH_SMOOTH = 3

# Signal Thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
STOCH_OVERSOLD = 20
STOCH_OVERBOUGHT = 80

# Database
DATABASE_PATH = 'trading_data/athena_bot.db'

# Logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'logs/athena_bot.log'
