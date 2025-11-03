"""
Athena Bot - Simple Launcher
Uses Multi-Strategy Analyzer to send signals to Discord
Signal-only mode (no trading)
"""

import asyncio
import discord
from discord.ext import tasks
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from binance_client import BinanceFuturesClient
from multi_strategy_analyzer import MultiStrategySignalAnalyzer
from logger import get_logger

load_dotenv()
log = get_logger('AthenaBot')

class AthenaSignalBot:
    """Simple signal-only bot"""
    
    def __init__(self):
        """Initialize bot"""
        self.discord_token = os.getenv('DISCORD_BOT_TOKEN')
        self.channel_id = int(os.getenv('SIGNAL_CHANNEL_ID', '0'))
        
        # Initialize Binance client
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        testnet = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
        
        self.client = BinanceFuturesClient(api_key, api_secret, testnet=testnet)
        self.analyzer = MultiStrategySignalAnalyzer(self.client)
        
        # Discord bot
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = discord.Client(intents=intents)
        
        # Symbols to track
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT']
        
        # Setup events
        @self.bot.event
        async def on_ready():
            log.info(f'✅ Bot logged in as {self.bot.user}')
            log.info(f'📢 Sending signals to channel: {self.channel_id}')
            log.info(f'🔍 Tracking symbols: {", ".join(self.symbols)}')
            self.monitor_markets.start()
        
        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return
            
            # Simple ping command
            if message.content.lower() == '!ping':
                await message.channel.send('🤖 Athena Bot Online! Signal-only mode activated.')
            
            # Status command
            elif message.content.lower() == '!status':
                await self.send_status(message.channel)
        
    @tasks.loop(minutes=15)
    async def monitor_markets(self):
        """Check markets every 15 minutes"""
        log.info("=" * 80)
        log.info(f"🔍 Market Scan Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log.info("=" * 80)
        
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            log.error(f"❌ Could not find channel: {self.channel_id}")
            return
        
        signals_found = 0
        
        for symbol in self.symbols:
            try:
                log.info(f"\n📊 Analyzing {symbol}...")
                
                result = self.analyzer.analyze_symbol(symbol, include_scalping=False)
                
                if result and result['signal'] in ['BUY', 'SELL']:
                    # Generate Discord message
                    message = self.analyzer.format_discord_message(result)
                    
                    # Send to Discord
                    await channel.send(message)
                    log.info(f"📢 {result['signal']} signal sent for {symbol}")
                    signals_found += 1
                    
                    # Small delay between signals
                    await asyncio.sleep(2)
                else:
                    log.info(f"⏸️  {symbol}: HOLD - no signal")
                    
            except Exception as e:
                log.error(f"❌ Error analyzing {symbol}: {e}")
                continue
        
        log.info("=" * 80)
        log.info(f"✅ Scan complete! {signals_found} signals generated")
        log.info(f"⏰ Next scan in 15 minutes")
        log.info("=" * 80)
    
    async def send_status(self, channel):
        """Send bot status"""
        try:
            balance = self.client.get_account_balance()
            usdt = balance.get('USDT', {}).get('wallet_balance', 0)
            
            status_msg = (
                "```\n"
                "🤖 ATHENA BOT STATUS\n"
                "=" * 40 + "\n"
                f"📊 Exchange: Binance Testnet\n"
                f"💰 Balance: {usdt:.2f} USDT\n"
                f"🔍 Tracking: {len(self.symbols)} symbols\n"
                f"📢 Mode: Signal-Only (No Trading)\n"
                f"⏰ Scan Interval: 15 minutes\n"
                f"🧠 Strategies: 7 active\n"
                "=" * 40 + "\n"
                "```"
            )
            
            await channel.send(status_msg)
            
        except Exception as e:
            log.error(f"Error sending status: {e}")
            await channel.send(f"❌ Error getting status: {str(e)}")
    
    def run(self):
        """Start the bot"""
        log.info("=" * 80)
        log.info("🚀 ATHENA BOT STARTING")
        log.info("=" * 80)
        log.info(f"📊 Exchange: Binance Testnet")
        log.info(f"📢 Signal Channel: {self.channel_id}")
        log.info(f"🔍 Symbols: {', '.join(self.symbols)}")
        log.info(f"⏰ Check Interval: 15 minutes")
        log.info(f"🧠 Strategies: Multi-Strategy (7 strategies)")
        log.info(f"🔒 Mode: SIGNAL-ONLY (No Trading)")
        log.info("=" * 80)
        
        try:
            self.bot.run(self.discord_token)
        except KeyboardInterrupt:
            log.info("\n👋 Bot stopped by user")
        except Exception as e:
            log.error(f"❌ Bot error: {e}")


if __name__ == "__main__":
    bot = AthenaSignalBot()
    bot.run()
