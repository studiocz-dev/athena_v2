"""
Automated Trading System with Performance Tracking
Monitors symbols, sends signals to Discord, places orders on testnet, tracks performance
"""

import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import sqlite3
from pathlib import Path

from binance_client import BinanceFuturesClient
from signal_analyzer_enhanced import EnhancedSignalAnalyzer
from strategies_enhanced import OptimizedStrategyFactory
from logger import get_logger
import config

logger = get_logger('AutoTrader')


class PerformanceTracker:
    """Track trading performance in SQLite database"""
    
    def __init__(self, db_path: str = "trading_data/performance.db"):
        self.db_path = db_path
        Path("trading_data").mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                signal TEXT NOT NULL,
                entry_time TIMESTAMP NOT NULL,
                entry_price REAL NOT NULL,
                quantity REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                signal_strength TEXT,
                stars INTEGER,
                exit_time TIMESTAMP,
                exit_price REAL,
                exit_reason TEXT,
                pnl REAL,
                pnl_percent REAL,
                status TEXT DEFAULT 'OPEN'
            )
        """)
        
        # Daily stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                largest_win REAL DEFAULT 0,
                largest_loss REAL DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Performance database initialized: {self.db_path}")
    
    def add_trade(self, trade_data: Dict) -> int:
        """Add a new trade to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trades (
                symbol, signal, entry_time, entry_price, quantity,
                stop_loss, take_profit, signal_strength, stars, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
        """, (
            trade_data['symbol'],
            trade_data['signal'],
            trade_data['entry_time'],
            trade_data['entry_price'],
            trade_data['quantity'],
            trade_data['stop_loss'],
            trade_data['take_profit'],
            trade_data.get('signal_strength', 'UNKNOWN'),
            trade_data.get('stars', 0)
        ))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Trade #{trade_id} added to database: {trade_data['symbol']} {trade_data['signal']}")
        return trade_id
    
    def close_trade(self, trade_id: int, exit_price: float, exit_reason: str) -> Dict:
        """Close a trade and calculate P&L"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get trade details
        cursor.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
        trade = cursor.fetchone()
        
        if not trade:
            conn.close()
            return None
        
        # Calculate P&L
        entry_price = trade[4]
        quantity = trade[5]
        signal = trade[2]
        
        if signal == 'BUY':
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100
        else:  # SELL
            pnl_percent = ((entry_price - exit_price) / entry_price) * 100
        
        pnl = (pnl_percent / 100) * (entry_price * quantity)
        
        # Update trade
        cursor.execute("""
            UPDATE trades 
            SET exit_time = ?, exit_price = ?, exit_reason = ?,
                pnl = ?, pnl_percent = ?, status = 'CLOSED'
            WHERE id = ?
        """, (datetime.now(), exit_price, exit_reason, pnl, pnl_percent, trade_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Trade #{trade_id} closed: {exit_reason}, P&L: ${pnl:.2f} ({pnl_percent:.2f}%)")
        
        return {
            'trade_id': trade_id,
            'symbol': trade[1],
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'exit_reason': exit_reason
        }
    
    def get_open_trades(self) -> List[Dict]:
        """Get all open trades"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM trades WHERE status = 'OPEN'")
        trades = cursor.fetchall()
        conn.close()
        
        return [self._trade_to_dict(t) for t in trades]
    
    def get_daily_performance(self, date: str = None) -> Dict:
        """Get performance for specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(pnl) as total_pnl,
                MAX(pnl) as largest_win,
                MIN(pnl) as largest_loss
            FROM trades
            WHERE DATE(entry_time) = ? AND status = 'CLOSED'
        """, (date,))
        
        result = cursor.fetchone()
        conn.close()
        
        total_trades = result[0] or 0
        winning_trades = result[1] or 0
        losing_trades = result[2] or 0
        total_pnl = result[3] or 0
        largest_win = result[4] or 0
        largest_loss = result[5] or 0
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'date': date,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'largest_win': largest_win,
            'largest_loss': largest_loss
        }
    
    def get_all_time_stats(self) -> Dict:
        """Get all-time statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(pnl) as total_pnl,
                AVG(CASE WHEN pnl > 0 THEN pnl ELSE NULL END) as avg_win,
                AVG(CASE WHEN pnl < 0 THEN pnl ELSE NULL END) as avg_loss,
                MAX(pnl) as best_trade,
                MIN(pnl) as worst_trade
            FROM trades
            WHERE status = 'CLOSED'
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        total_trades = result[0] or 0
        winning_trades = result[1] or 0
        total_pnl = result[2] or 0
        avg_win = result[3] or 0
        avg_loss = result[4] or 0
        best_trade = result[5] or 0
        worst_trade = result[6] or 0
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'best_trade': best_trade,
            'worst_trade': worst_trade
        }
    
    def _trade_to_dict(self, trade_tuple) -> Dict:
        """Convert database tuple to dictionary"""
        return {
            'id': trade_tuple[0],
            'symbol': trade_tuple[1],
            'signal': trade_tuple[2],
            'entry_time': trade_tuple[3],
            'entry_price': trade_tuple[4],
            'quantity': trade_tuple[5],
            'stop_loss': trade_tuple[6],
            'take_profit': trade_tuple[7],
            'signal_strength': trade_tuple[8],
            'stars': trade_tuple[9],
            'exit_time': trade_tuple[10],
            'exit_price': trade_tuple[11],
            'exit_reason': trade_tuple[12],
            'pnl': trade_tuple[13],
            'pnl_percent': trade_tuple[14],
            'status': trade_tuple[15]
        }


class AutomatedTradingBot(commands.Bot):
    """Discord bot with automated trading"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize components
        self.client = BinanceFuturesClient(
            config.BINANCE_API_KEY,
            config.BINANCE_API_SECRET,
            testnet=config.BINANCE_TESTNET
        )
        
        self.analyzer = EnhancedSignalAnalyzer(
            self.client,
            use_mtf=True,  # Use multi-timeframe analysis
            primary_timeframe="15m",
            confirmation_timeframes=["1h", "4h"]
        )
        
        # Use optimized strategy (don't override, analyzer handles it internally)
        
        self.tracker = PerformanceTracker()
        
        # Expanded watchlist - 14 symbols for better opportunities
        self.watchlist = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT',  # Major coins
            'ADAUSDT', 'AVAXUSDT', 'MATICUSDT', 'DOTUSDT',  # Large caps
            'LINKUSDT', 'ATOMUSDT', 'NEARUSDT', 'APTUSDT',  # Mid caps
            'ARBUSDT', 'OPUSDT'  # L2 coins
        ]
        
        # Settings
        self.min_signal_stars = 3  # Only trade 3+ star signals
        self.position_size_usdt = 100  # $100 per trade
        self.max_positions = 3  # Max 3 concurrent positions
        
        # Volatility filter settings
        self.use_volatility_filter = True  # Enable ATR-based filtering
        self.min_atr_percent = 1.25  # Minimum 1.25% ATR to consider trading (lowered for more signals)
        
        # Discord channel IDs
        self.signals_channel_id = 1423658108286275717  # Signals channel
        self.reports_channel_id = 1432616229159571476  # Reports channel
        
        logger.info("✅ Automated Trading Bot initialized")
    
    async def on_ready(self):
        """Bot ready event"""
        logger.info("\n" + "=" * 60)
        logger.info("🤖 ATHENA V2 AUTOMATED TRADING BOT")
        logger.info("=" * 60)
        logger.info(f"✅ Bot logged in as: {self.user}")
        logger.info(f"📊 Watchlist: {', '.join(self.watchlist)}")
        logger.info(f"⭐ Min Signal Stars: {self.min_signal_stars}")
        logger.info(f"💰 Position Size: ${self.position_size_usdt} per trade")
        logger.info(f"📈 Max Positions: {self.max_positions}")
        logger.info(f"⏰ Scan Frequency: Every 15 minutes")
        logger.info(f"🎯 Position Check: Every 5 minutes")
        logger.info(f"📊 Daily Report: Every 24 hours")
        
        # Check channels
        signals_channel = self.get_channel(self.signals_channel_id)
        reports_channel = self.get_channel(self.reports_channel_id)
        
        if signals_channel:
            logger.info(f"📢 Signals Channel: #{signals_channel.name}")
        else:
            logger.warning(f"⚠️  Signals channel {self.signals_channel_id} not found!")
            
        if reports_channel:
            logger.info(f"📊 Reports Channel: #{reports_channel.name}")
        else:
            logger.warning(f"⚠️  Reports channel {self.reports_channel_id} not found!")
        
        logger.info("\n🔄 Starting background tasks...")
        
        # Start background tasks
        if not self.scan_and_trade.is_running():
            self.scan_and_trade.start()
            logger.info("✅ Scan & Trade task started (15 min interval)")
        
        if not self.check_positions.is_running():
            self.check_positions.start()
            logger.info("✅ Position Check task started (5 min interval)")
        
        if not self.send_daily_report.is_running():
            self.send_daily_report.start()
            logger.info("✅ Daily Report task started (24 hour interval)")
        
        logger.info("\n🚀 Bot is now running and monitoring markets!")
        logger.info("=" * 60)
    
    def check_volatility(self, symbol: str) -> tuple[bool, float]:
        """
        Check if symbol has sufficient volatility for trading
        Returns: (is_volatile_enough, atr_percent)
        """
        try:
            # Get 1-hour klines for ATR calculation
            klines = self.client.get_klines(symbol, '1h', limit=14)
            if not klines or len(klines) < 14:
                logger.warning(f"⚠️  Insufficient data for {symbol} volatility check")
                return False, 0.0
            
            # Calculate ATR (14-period)
            high_prices = [float(k[2]) for k in klines]
            low_prices = [float(k[3]) for k in klines]
            close_prices = [float(k[4]) for k in klines]
            
            true_ranges = []
            for i in range(1, len(klines)):
                high_low = high_prices[i] - low_prices[i]
                high_close = abs(high_prices[i] - close_prices[i-1])
                low_close = abs(low_prices[i] - close_prices[i-1])
                true_range = max(high_low, high_close, low_close)
                true_ranges.append(true_range)
            
            atr = sum(true_ranges) / len(true_ranges)
            current_price = close_prices[-1]
            atr_percent = (atr / current_price) * 100
            
            is_volatile = atr_percent >= self.min_atr_percent
            
            return is_volatile, atr_percent
            
        except Exception as e:
            logger.error(f"❌ Error checking volatility for {symbol}: {e}")
            return False, 0.0
    
    @tasks.loop(minutes=15)  # Scan every 15 minutes
    async def scan_and_trade(self):
        """Scan watchlist and execute trades on good signals"""
        try:
            logger.info("=" * 60)
            logger.info("🔍 SCANNING WATCHLIST FOR TRADING SIGNALS")
            logger.info(f"⏰ Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"📊 Symbols: {', '.join(self.watchlist)}")
            
            # Check if we have room for more positions
            open_trades = self.tracker.get_open_trades()
            logger.info(f"📈 Open Positions: {len(open_trades)}/{self.max_positions}")
            
            if len(open_trades) >= self.max_positions:
                logger.warning(f"⚠️  Max positions reached ({self.max_positions}), skipping scan")
                logger.info("=" * 60)
                return
            
            # Scan all symbols
            signals_found = 0
            for i, symbol in enumerate(self.watchlist, 1):
                try:
                    logger.info(f"\n📌 [{i}/{len(self.watchlist)}] Analyzing {symbol}...")
                    
                    # Check volatility first (if filter enabled)
                    if self.use_volatility_filter:
                        is_volatile, atr_percent = self.check_volatility(symbol)
                        logger.info(f"   📊 ATR: {atr_percent:.2f}% (min: {self.min_atr_percent}%)")
                        
                        if not is_volatile:
                            logger.info(f"   ⚠️  Low volatility - skipping (ranging market)")
                            continue
                        else:
                            logger.info(f"   ✅ Sufficient volatility - analyzing signals")
                    
                    # Get signal
                    analysis = self.analyzer.analyze_symbol(symbol)
                    
                    if 'error' in analysis:
                        logger.error(f"❌ Error in {symbol}: {analysis['error']}")
                        continue
                    
                    signal = analysis['signal']
                    stars = analysis.get('stars', 0)
                    current_price = analysis.get('current_price', 0)
                    
                    logger.info(f"   Signal: {signal} {'⭐' * stars} ({stars} stars)")
                    logger.info(f"   Price: ${current_price:.4f}")
                    
                    # Check if signal meets criteria
                    if signal in ['BUY', 'SELL'] and stars >= self.min_signal_stars:
                        # Check if already have position in this symbol
                        if any(t['symbol'] == symbol for t in open_trades):
                            logger.info(f"   ℹ️  Already have open position in {symbol}, skipping")
                            continue
                        
                        signals_found += 1
                        logger.info(f"   ✅ VALID SIGNAL! Executing {signal} trade...")
                        
                        # Execute trade
                        await self.execute_trade(analysis)
                        
                        # Send signal to Discord
                        await self.send_signal_notification(analysis)
                        
                    else:
                        if signal == 'HOLD':
                            logger.info(f"   ⏸️  No trade signal (HOLD)")
                        else:
                            logger.info(f"   ⚠️  Signal below threshold ({stars} < {self.min_signal_stars} stars)")
                        
                except Exception as e:
                    logger.error(f"❌ Error analyzing {symbol}: {str(e)}", exc_info=True)
                    continue
            
            logger.info(f"\n✅ Scan complete: {signals_found} valid signal(s) found")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error in scan_and_trade: {e}")
    
    @tasks.loop(minutes=5)  # Check positions every 5 minutes
    async def check_positions(self):
        """Check open positions for TP/SL hits"""
        try:
            open_trades = self.tracker.get_open_trades()
            
            if not open_trades:
                logger.debug("🔍 Position check: No open positions")
                return
            
            logger.info("\n" + "=" * 60)
            logger.info(f"🎯 CHECKING POSITIONS - {len(open_trades)} open")
            logger.info(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            for i, trade in enumerate(open_trades, 1):
                try:
                    symbol = trade['symbol']
                    entry_price = trade['entry_price']
                    stop_loss = trade['stop_loss']
                    take_profit = trade['take_profit']
                    signal = trade['signal']
                    
                    logger.info(f"\n📊 [{i}/{len(open_trades)}] {symbol} ({signal})")
                    logger.info(f"   Entry: ${entry_price:.4f}")
                    
                    # Get current price
                    ticker = self.client.client.futures_symbol_ticker(symbol=symbol)
                    current_price = float(ticker['price'])
                    
                    # Calculate P&L percentage
                    if signal == 'BUY':
                        pnl_pct = ((current_price - entry_price) / entry_price) * 100
                        tp_distance = ((take_profit - current_price) / current_price) * 100
                        sl_distance = ((current_price - stop_loss) / current_price) * 100
                    else:  # SELL
                        pnl_pct = ((entry_price - current_price) / entry_price) * 100
                        tp_distance = ((current_price - take_profit) / current_price) * 100
                        sl_distance = ((stop_loss - current_price) / current_price) * 100
                    
                    pnl_emoji = "🟢" if pnl_pct >= 0 else "🔴"
                    logger.info(f"   Current: ${current_price:.4f} {pnl_emoji} ({pnl_pct:+.2f}%)")
                    logger.info(f"   TP: ${take_profit:.4f} ({tp_distance:.2f}% away)")
                    logger.info(f"   SL: ${stop_loss:.4f} ({sl_distance:.2f}% away)")
                    
                    # Check if TP or SL hit
                    hit_tp = False
                    hit_sl = False
                    
                    if signal == 'BUY':
                        if current_price >= take_profit:
                            hit_tp = True
                        elif current_price <= stop_loss:
                            hit_sl = True
                    else:  # SELL
                        if current_price <= take_profit:
                            hit_tp = True
                        elif current_price >= stop_loss:
                            hit_sl = True
                    
                    if hit_tp or hit_sl:
                        exit_reason = 'TP' if hit_tp else 'SL'
                        emoji = "🎯" if hit_tp else "🛑"
                        logger.info(f"   {emoji} {exit_reason} HIT! Closing position...")
                        
                        result = self.tracker.close_trade(trade['id'], current_price, exit_reason)
                        
                        if result:
                            await self.send_exit_notification(result)
                            logger.info(f"   ✅ Position closed: P&L = ${result['pnl']:+.2f} ({result['pnl_percent']:+.2f}%)")
                    else:
                        logger.info(f"   ⏳ Position still open")
                
                except Exception as e:
                    logger.error(f"❌ Error checking position {trade['symbol']}: {str(e)}", exc_info=True)
                    continue
            
            logger.info("\n✅ Position check complete")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error in check_positions: {str(e)}", exc_info=True)
    
    @tasks.loop(hours=24)  # Send report every 24 hours
    async def send_daily_report(self):
        """Send daily performance report to Discord"""
        try:
            logger.info("\n" + "=" * 60)
            logger.info("📊 GENERATING DAILY PERFORMANCE REPORT")
            logger.info(f"⏰ Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get today's performance
            today_stats = self.tracker.get_daily_performance()
            
            # Get all-time stats
            all_time_stats = self.tracker.get_all_time_stats()
            
            # Create embed
            embed = discord.Embed(
                title="📊 Daily Performance Report",
                description=f"Report for {today_stats['date']}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Today's stats
            pnl_color = "🟢" if today_stats['total_pnl'] >= 0 else "🔴"
            embed.add_field(
                name="📈 Today's Performance",
                value=f"""
**Trades:** {today_stats['total_trades']}
**Won:** {today_stats['winning_trades']} | **Lost:** {today_stats['losing_trades']}
**Win Rate:** {today_stats['win_rate']:.1f}%
**Total P&L:** {pnl_color} ${today_stats['total_pnl']:.2f}
**Best Trade:** ${today_stats['largest_win']:.2f}
**Worst Trade:** ${today_stats['largest_loss']:.2f}
                """,
                inline=False
            )
            
            # All-time stats
            total_pnl_color = "🟢" if all_time_stats['total_pnl'] >= 0 else "🔴"
            embed.add_field(
                name="🏆 All-Time Statistics",
                value=f"""
**Total Trades:** {all_time_stats['total_trades']}
**Win Rate:** {all_time_stats['win_rate']:.1f}%
**Total P&L:** {total_pnl_color} ${all_time_stats['total_pnl']:.2f}
**Avg Win:** ${all_time_stats['avg_win']:.2f}
**Avg Loss:** ${all_time_stats['avg_loss']:.2f}
**Best Trade:** ${all_time_stats['best_trade']:.2f}
**Worst Trade:** ${all_time_stats['worst_trade']:.2f}
                """,
                inline=False
            )
            
            # Open positions
            open_trades = self.tracker.get_open_trades()
            if open_trades:
                positions_text = "\n".join([
                    f"**{t['symbol']}** {t['signal']} @ ${t['entry_price']:.2f} ({t['stars']}⭐)"
                    for t in open_trades
                ])
            else:
                positions_text = "No open positions"
            
            embed.add_field(
                name=f"💼 Open Positions ({len(open_trades)})",
                value=positions_text,
                inline=False
            )
            
            embed.set_footer(text="Athena Auto-Trading Bot | Testnet")
            
            # Send to reports channel
            if self.reports_channel_id:
                channel = self.get_channel(self.reports_channel_id)
                if channel:
                    await channel.send(embed=embed)
                    logger.info("Daily report sent to Discord")
            else:
                logger.warning("Reports channel not set")
            
        except Exception as e:
            logger.error(f"Error sending daily report: {e}")
    
    async def execute_trade(self, analysis: Dict):
        """Execute trade on testnet"""
        try:
            symbol = analysis['symbol']
            signal = analysis['signal']
            current_price = analysis['current_price']
            stop_loss = analysis['stop_loss']
            take_profit = analysis['take_profit']
            stars = analysis.get('stars', 0)
            
            logger.info("\n" + "-" * 60)
            logger.info(f"🎯 EXECUTING TRADE")
            logger.info(f"Symbol: {symbol}")
            logger.info(f"Signal: {signal} {'⭐' * stars}")
            logger.info(f"Entry Price: ${current_price:.4f}")
            
            # Calculate quantity
            quantity = self.position_size_usdt / current_price
            quantity = round(quantity, 3)  # Round to 3 decimals
            position_value = quantity * current_price
            
            logger.info(f"Position Size: {quantity} {symbol} (${position_value:.2f})")
            logger.info(f"Stop Loss: ${stop_loss:.4f} ({((stop_loss - current_price) / current_price * 100):+.2f}%)")
            logger.info(f"Take Profit: ${take_profit:.4f} ({((take_profit - current_price) / current_price * 100):+.2f}%)")
            
            # Calculate risk/reward
            if signal == 'BUY':
                risk = current_price - stop_loss
                reward = take_profit - current_price
            else:  # SELL
                risk = stop_loss - current_price
                reward = current_price - take_profit
            
            risk_reward = reward / risk if risk > 0 else 0
            logger.info(f"Risk/Reward: {risk_reward:.2f}")
            
            # Place order on testnet
            logger.info(f"\n📤 Placing {signal} order on TESTNET...")
            
            # Note: For testnet, we'll simulate the order
            # In live trading, you'd use: self.client.place_market_order(symbol, signal, quantity)
            
            # Add to database
            trade_data = {
                'symbol': symbol,
                'signal': signal,
                'entry_time': datetime.now(),
                'entry_price': current_price,
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'signal_strength': analysis.get('signal_strength', 'UNKNOWN'),
                'stars': stars
            }
            
            trade_id = self.tracker.add_trade(trade_data)
            logger.info(f"✅ Trade #{trade_id} executed successfully!")
            logger.info(f"💾 Trade saved to database")
            logger.info("-" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error executing trade: {str(e)}", exc_info=True)
    
    async def send_signal_notification(self, analysis: Dict):
        """Send signal notification to Discord"""
        try:
            symbol = analysis['symbol']
            signal = analysis['signal']
            stars = analysis.get('stars', 0)
            current_price = analysis['current_price']
            stop_loss = analysis['stop_loss']
            take_profit = analysis['take_profit']
            
            # Create embed
            color = discord.Color.green() if signal == 'BUY' else discord.Color.red()
            embed = discord.Embed(
                title=f"{'🟢 BUY' if signal == 'BUY' else '🔴 SELL'} Signal - {symbol}",
                description=f"{'⭐' * stars} Signal Strength: {analysis.get('signal_strength', 'UNKNOWN')}",
                color=color,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="Entry Price", value=f"${current_price:.4f}", inline=True)
            embed.add_field(name="Stop Loss", value=f"${stop_loss:.4f}", inline=True)
            embed.add_field(name="Take Profit", value=f"${take_profit:.4f}", inline=True)
            
            if analysis.get('mtf_enabled'):
                embed.add_field(
                    name="Trend Analysis",
                    value=f"Overall: {analysis.get('overall_trend', 'N/A')}\nHTF Confirmation: {'✅' if analysis.get('mtf_confirmation') else '❌'}",
                    inline=False
                )
            
            embed.add_field(
                name="Recommendation",
                value=analysis.get('recommendation', 'Trade signal detected'),
                inline=False
            )
            
            embed.set_footer(text="Order placed on Testnet | Auto-Trading Active")
            
            # Send to signals channel
            if self.signals_channel_id:
                channel = self.get_channel(self.signals_channel_id)
                if channel:
                    await channel.send(embed=embed)
                    logger.info(f"Signal notification sent for {symbol}")
            else:
                logger.warning("Signals channel not set")
            
        except Exception as e:
            logger.error(f"Error sending signal notification: {e}")
    
    async def send_exit_notification(self, result: Dict):
        """Send trade exit notification"""
        try:
            symbol = result['symbol']
            pnl = result['pnl']
            pnl_percent = result['pnl_percent']
            exit_reason = result['exit_reason']
            
            color = discord.Color.green() if pnl > 0 else discord.Color.red()
            emoji = "✅" if pnl > 0 else "❌"
            
            embed = discord.Embed(
                title=f"{emoji} Trade Closed - {symbol}",
                description=f"Exit Reason: {exit_reason}",
                color=color,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="P&L", value=f"${pnl:.2f}", inline=True)
            embed.add_field(name="Return", value=f"{pnl_percent:.2f}%", inline=True)
            
            embed.set_footer(text="Testnet Trading")
            
            # Send to signals channel
            if self.signals_channel_id:
                channel = self.get_channel(self.signals_channel_id)
                if channel:
                    await channel.send(embed=embed)
                    logger.info(f"Exit notification sent for {symbol}")
            
        except Exception as e:
            logger.error(f"Error sending exit notification: {e}")


def main():
    """Run the automated trading bot"""
    logger.info("\n" + "🚀" * 30)
    logger.info("ATHENA V2 - AUTOMATED TRADING BOT")
    logger.info("Starting initialization...")
    logger.info("🚀" * 30 + "\n")
    
    try:
        bot = AutomatedTradingBot()
        logger.info("✅ Bot instance created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create bot instance: {str(e)}", exc_info=True)
        return
    
    @bot.command()
    async def set_signals_channel(ctx):
        """Set current channel as signals channel"""
        bot.signals_channel_id = ctx.channel.id
        await ctx.send(f"✅ Signals channel set to: {ctx.channel.mention}")
        logger.info(f"Signals channel set to: {ctx.channel.id}")
    
    @bot.command()
    async def set_reports_channel(ctx):
        """Set current channel as reports channel"""
        bot.reports_channel_id = ctx.channel.id
        await ctx.send(f"✅ Reports channel set to: {ctx.channel.mention}")
        logger.info(f"Reports channel set to: {ctx.channel.id}")
    
    @bot.command()
    async def status(ctx):
        """Get current bot status"""
        open_trades = bot.tracker.get_open_trades()
        today_stats = bot.tracker.get_daily_performance()
        
        embed = discord.Embed(
            title="🤖 Bot Status",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Watchlist", value=", ".join(bot.watchlist), inline=False)
        embed.add_field(name="Open Positions", value=f"{len(open_trades)}/{bot.max_positions}", inline=True)
        embed.add_field(name="Min Signal Stars", value=f"{bot.min_signal_stars}⭐", inline=True)
        embed.add_field(name="Today's P&L", value=f"${today_stats['total_pnl']:.2f}", inline=True)
        
        await ctx.send(embed=embed)
    
    @bot.command()
    async def report(ctx):
        """Get immediate performance report"""
        logger.info(f"📊 Manual report requested by {ctx.author}")
        await bot.send_daily_report()
        await ctx.send("✅ Report generated!")
    
    @bot.command()
    async def stop(ctx):
        """Emergency stop - close all positions"""
        logger.warning(f"🛑 EMERGENCY STOP requested by {ctx.author}")
        open_trades = bot.tracker.get_open_trades()
        
        if not open_trades:
            await ctx.send("ℹ️ No open positions to close")
            return
        
        closed = 0
        for trade in open_trades:
            try:
                # Get current price and close
                ticker = bot.client.client.futures_symbol_ticker(symbol=trade['symbol'])
                current_price = float(ticker['price'])
                bot.tracker.close_trade(trade['id'], current_price, 'MANUAL_STOP')
                closed += 1
                logger.info(f"🛑 Closed {trade['symbol']} at ${current_price:.4f}")
            except Exception as e:
                logger.error(f"Error closing {trade['symbol']}: {e}")
        
        await ctx.send(f"🛑 Emergency stop: Closed {closed} position(s)")
        logger.warning(f"🛑 Emergency stop complete: {closed} positions closed")
    
    # Run bot
    logger.info("\n🔌 Connecting to Discord...")
    try:
        bot.run(config.DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Keyboard interrupt received - shutting down gracefully...")
    except Exception as e:
        logger.error(f"\n\n❌ Bot crashed: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
