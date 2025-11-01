"""
Athena Discord Trading Bot
Main bot implementation with all commands
"""
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from typing import Optional, List
import pandas as pd
from datetime import datetime

from binance_client import BinanceFuturesClient
from signal_analyzer import SignalAnalyzer
from strategies import get_strategy
from logger import get_logger
import config

log = get_logger('DiscordBot')


class AthenaBot(commands.Bot):
    """Athena Trading Bot for Discord"""
    
    def __init__(self):
        """Initialize the bot"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Initialize Binance client
        self.binance_client = None
        self.signal_analyzer = None
        self.trading_enabled = config.TRADING_ENABLED
        
        # Tracked symbols
        self.tracked_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
            'ADAUSDT', 'DOGEUSDT', 'MATICUSDT', 'DOTUSDT', 'LINKUSDT'
        ]
        
        # Active monitoring
        self.monitoring_active = False
        self.signal_channel_id = None
    
    async def setup_hook(self):
        """Setup hook called when bot starts"""
        log.info("Setting up Athena Bot...")
        
        # Initialize Binance client
        try:
            self.binance_client = BinanceFuturesClient(
                config.BINANCE_API_KEY,
                config.BINANCE_API_SECRET,
                config.BINANCE_TESTNET
            )
            self.signal_analyzer = SignalAnalyzer(self.binance_client)
            log.info("Binance client initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize Binance client: {e}")
        
        # Start background tasks
        if not self.monitor_signals.is_running():
            self.monitor_signals.start()
        
        # Sync commands
        try:
            synced = await self.tree.sync()
            log.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            log.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        log.info(f'Bot logged in as {self.user.name} ({self.user.id})')
        log.info(f'Connected to {len(self.guilds)} guild(s)')
        
        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Binance Futures 📈"
            )
        )
    
    @tasks.loop(minutes=15)
    async def monitor_signals(self):
        """Background task to monitor for trading signals"""
        if not self.monitoring_active or not self.signal_channel_id:
            return
        
        try:
            channel = self.get_channel(int(self.signal_channel_id))
            if not channel:
                return
            
            log.info("Scanning for trading signals...")
            
            # Scan symbols with EMA Cross strategy
            signals = self.signal_analyzer.scan_multiple_symbols(
                self.tracked_symbols,
                'EMA_CROSS',
                config.DEFAULT_INTERVAL,
                min_signal_strength=60.0
            )
            
            # Send signals to channel
            for signal in signals[:3]:  # Top 3 signals
                embed = self.create_signal_embed(signal)
                await channel.send(embed=embed)
                
        except Exception as e:
            log.error(f"Error in monitor_signals: {e}")
    
    @monitor_signals.before_loop
    async def before_monitor_signals(self):
        """Wait until bot is ready"""
        await self.wait_until_ready()
    
    def create_signal_embed(self, signal: dict) -> discord.Embed:
        """Create a Discord embed for a signal"""
        side = signal.get('signal', 'NONE')
        symbol = signal.get('symbol', 'UNKNOWN')
        strength = signal.get('strength', 0)
        strategy = signal.get('strategy', 'UNKNOWN')
        
        # Color based on signal
        color = discord.Color.green() if side == 'LONG' else discord.Color.red()
        
        embed = discord.Embed(
            title=f"🎯 {side} Signal: {symbol}",
            description=f"Strategy: **{strategy}**",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Add fields
        embed.add_field(
            name="💪 Signal Strength",
            value=f"{strength}%",
            inline=True
        )
        
        embed.add_field(
            name="💰 Current Price",
            value=f"${signal.get('price', 0):.4f}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Interval",
            value=signal.get('interval', config.DEFAULT_INTERVAL),
            inline=True
        )
        
        # Add strategy-specific data
        if 'entry_price' in signal:
            embed.add_field(
                name="🎯 Entry Price",
                value=f"${signal['entry_price']:.4f}",
                inline=True
            )
        
        if 'stop_loss' in signal:
            embed.add_field(
                name="🛑 Stop Loss",
                value=f"${signal['stop_loss']:.4f}",
                inline=True
            )
        
        if 'take_profit' in signal:
            embed.add_field(
                name="✅ Take Profit",
                value=f"${signal['take_profit']:.4f}",
                inline=True
            )
        
        if 'risk_reward_ratio' in signal:
            embed.add_field(
                name="⚖️ Risk:Reward",
                value=f"1:{signal['risk_reward_ratio']}",
                inline=True
            )
        
        embed.set_footer(text="Athena Trading Bot | For informational purposes only")
        
        return embed


# Initialize bot
bot = AthenaBot()


# ============================================================================
# SLASH COMMANDS
# ============================================================================

@bot.tree.command(name="signal", description="Get a trading signal for a symbol")
@app_commands.describe(
    symbol="Trading symbol (e.g., BTCUSDT)",
    strategy="Trading strategy to use",
    interval="Candle interval (e.g., 15m, 1h, 4h)"
)
async def signal_command(
    interaction: discord.Interaction,
    symbol: str,
    strategy: str = "EMA_CROSS",
    interval: str = "15m"
):
    """Get a trading signal for a specific symbol"""
    await interaction.response.defer()
    
    try:
        symbol = symbol.upper()
        if not symbol.endswith('USDT'):
            symbol += 'USDT'
        
        # Get signal with levels
        signal = bot.signal_analyzer.get_signal_with_levels(
            symbol,
            strategy,
            interval,
            config.DEFAULT_LEVERAGE
        )
        
        if not signal or not signal.get('signal'):
            await interaction.followup.send(
                f"❌ No signal found for {symbol} using {strategy} strategy.",
                ephemeral=True
            )
            return
        
        # Create and send embed
        embed = bot.create_signal_embed(signal)
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        log.error(f"Error in signal command: {e}")
        await interaction.followup.send(
            f"❌ Error getting signal: {str(e)}",
            ephemeral=True
        )


@bot.tree.command(name="scan", description="Scan multiple symbols for trading signals")
@app_commands.describe(
    strategy="Trading strategy to use",
    interval="Candle interval",
    min_strength="Minimum signal strength (0-100)"
)
async def scan_command(
    interaction: discord.Interaction,
    strategy: str = "EMA_CROSS",
    interval: str = "15m",
    min_strength: float = 50.0
):
    """Scan multiple symbols for signals"""
    await interaction.response.defer()
    
    try:
        signals = bot.signal_analyzer.scan_multiple_symbols(
            bot.tracked_symbols,
            strategy,
            interval,
            min_strength
        )
        
        if not signals:
            await interaction.followup.send(
                f"❌ No signals found with minimum strength of {min_strength}%",
                ephemeral=True
            )
            return
        
        # Create summary embed
        embed = discord.Embed(
            title=f"📊 Market Scan Results",
            description=f"Strategy: **{strategy}** | Interval: **{interval}**",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        for i, signal in enumerate(signals[:10], 1):
            side = signal.get('signal', 'NONE')
            symbol = signal.get('symbol', 'UNKNOWN')
            strength = signal.get('strength', 0)
            price = signal.get('price', 0)
            
            emoji = "🟢" if side == "LONG" else "🔴"
            
            embed.add_field(
                name=f"{emoji} {i}. {symbol}",
                value=f"{side} | Strength: {strength}% | ${price:.4f}",
                inline=False
            )
        
        embed.set_footer(text=f"Found {len(signals)} signal(s)")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        log.error(f"Error in scan command: {e}")
        await interaction.followup.send(
            f"❌ Error scanning: {str(e)}",
            ephemeral=True
        )


@bot.tree.command(name="balance", description="Get your Binance Futures account balance")
async def balance_command(interaction: discord.Interaction):
    """Get account balance"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        balances = bot.binance_client.get_account_balance()
        
        if not balances:
            await interaction.followup.send(
                "❌ Unable to fetch balance or no assets found.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="💰 Futures Account Balance",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        total_balance = 0
        for asset, data in balances.items():
            wallet_balance = data['wallet_balance']
            unrealized_pnl = data['unrealized_pnl']
            
            total_balance += wallet_balance
            
            embed.add_field(
                name=f"{asset}",
                value=f"Balance: {wallet_balance:.2f}\nUnrealized P&L: {unrealized_pnl:.2f}",
                inline=True
            )
        
        embed.description = f"**Total Balance: ${total_balance:.2f}**"
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        log.error(f"Error in balance command: {e}")
        await interaction.followup.send(
            f"❌ Error getting balance: {str(e)}",
            ephemeral=True
        )


@bot.tree.command(name="positions", description="View your open positions")
async def positions_command(interaction: discord.Interaction):
    """Get open positions"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        positions = bot.binance_client.get_position_info()
        
        if not positions:
            await interaction.followup.send(
                "📭 No open positions found.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📊 Open Positions",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        for pos in positions:
            side = pos['side']
            symbol = pos['symbol']
            size = abs(pos['position_amount'])
            entry = pos['entry_price']
            mark = pos['mark_price']
            pnl = pos['unrealized_pnl']
            leverage = pos['leverage']
            
            pnl_pct = ((mark - entry) / entry * 100) if side == 'LONG' else ((entry - mark) / entry * 100)
            
            emoji = "🟢" if pnl > 0 else "🔴"
            
            value = f"Side: **{side}**\n"
            value += f"Size: {size}\n"
            value += f"Entry: ${entry:.4f}\n"
            value += f"Mark: ${mark:.4f}\n"
            value += f"Leverage: {leverage}x\n"
            value += f"P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)"
            
            embed.add_field(
                name=f"{emoji} {symbol}",
                value=value,
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        log.error(f"Error in positions command: {e}")
        await interaction.followup.send(
            f"❌ Error getting positions: {str(e)}",
            ephemeral=True
        )


@bot.tree.command(name="price", description="Get current price for a symbol")
@app_commands.describe(symbol="Trading symbol (e.g., BTCUSDT)")
async def price_command(interaction: discord.Interaction, symbol: str):
    """Get current price"""
    await interaction.response.defer()
    
    try:
        symbol = symbol.upper()
        if not symbol.endswith('USDT'):
            symbol += 'USDT'
        
        price = bot.binance_client.get_current_price(symbol)
        
        if not price:
            await interaction.followup.send(
                f"❌ Could not fetch price for {symbol}",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"💲 {symbol} Price",
            description=f"**${price:,.4f}**",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        log.error(f"Error in price command: {e}")
        await interaction.followup.send(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )


@bot.tree.command(name="monitor", description="Start/stop automatic signal monitoring")
@app_commands.describe(
    action="Start or stop monitoring",
    channel="Channel to send signals to"
)
async def monitor_command(
    interaction: discord.Interaction,
    action: str,
    channel: Optional[discord.TextChannel] = None
):
    """Toggle signal monitoring"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        if action.lower() == "start":
            if not channel:
                await interaction.followup.send(
                    "❌ Please specify a channel for signals.",
                    ephemeral=True
                )
                return
            
            bot.monitoring_active = True
            bot.signal_channel_id = str(channel.id)
            
            await interaction.followup.send(
                f"✅ Signal monitoring started! Signals will be sent to {channel.mention}",
                ephemeral=True
            )
            
        elif action.lower() == "stop":
            bot.monitoring_active = False
            bot.signal_channel_id = None
            
            await interaction.followup.send(
                "✅ Signal monitoring stopped.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ Invalid action. Use 'start' or 'stop'.",
                ephemeral=True
            )
            
    except Exception as e:
        log.error(f"Error in monitor command: {e}")
        await interaction.followup.send(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )


@bot.tree.command(name="strategies", description="List available trading strategies")
async def strategies_command(interaction: discord.Interaction):
    """List available strategies"""
    await interaction.response.defer()
    
    embed = discord.Embed(
        title="📚 Available Trading Strategies",
        description="Choose from these strategies when generating signals",
        color=discord.Color.purple(),
        timestamp=datetime.utcnow()
    )
    
    strategies_info = {
        "EMA_CROSS": "EMA crossover strategy (9/21)",
        "TRIPLE_EMA": "Triple EMA alignment (9/21/50)",
        "RSI_DIVERGENCE": "RSI divergence and extremes",
        "MACD_SIGNAL": "MACD signal line crossover",
        "STOCH_RSI": "Stochastic RSI crossovers",
        "BREAKOUT": "Price breakout with volume",
        "SUPPORT_RESISTANCE": "Support/Resistance bounces"
    }
    
    for strategy, description in strategies_info.items():
        embed.add_field(
            name=strategy,
            value=description,
            inline=False
        )
    
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    """Show help"""
    embed = discord.Embed(
        title="🤖 Athena Trading Bot - Help",
        description="Binance Futures Trading Signal Bot",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    commands_info = {
        "/signal": "Get a trading signal for a specific symbol",
        "/scan": "Scan multiple symbols for signals",
        "/price": "Get current price for a symbol",
        "/balance": "View your Binance Futures balance",
        "/positions": "View your open positions",
        "/monitor": "Start/stop automatic signal monitoring",
        "/strategies": "List all available trading strategies",
        "/help": "Show this help message"
    }
    
    for cmd, desc in commands_info.items():
        embed.add_field(
            name=cmd,
            value=desc,
            inline=False
        )
    
    embed.set_footer(text="⚠️ Trading involves risk. Use at your own discretion.")
    
    await interaction.followup.send(embed=embed)


# ============================================================================
# RUN BOT
# ============================================================================

def run_bot():
    """Run the Discord bot"""
    try:
        if not config.DISCORD_BOT_TOKEN:
            log.error("Discord bot token not found in environment variables!")
            return
        
        log.info("Starting Athena Discord Bot...")
        bot.run(config.DISCORD_BOT_TOKEN)
        
    except Exception as e:
        log.error(f"Failed to start bot: {e}")


if __name__ == "__main__":
    run_bot()
