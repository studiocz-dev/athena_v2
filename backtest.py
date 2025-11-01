"""
Backtesting Engine for Athena Trading Bot
Tests trading strategies against historical data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from tabulate import tabulate

from binance_client import BinanceFuturesClient
from strategies import get_strategy, calculate_stop_loss_take_profit
from signal_analyzer import SignalAnalyzer
from logger import get_logger
import config

log = get_logger('Backtester')


class Trade:
    """Represents a single trade"""
    
    def __init__(self, entry_time, entry_price, side, quantity, stop_loss, take_profit, strategy):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.side = side  # 'LONG' or 'SHORT'
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.strategy = strategy
        
        self.exit_time = None
        self.exit_price = None
        self.exit_reason = None  # 'TP', 'SL', or 'SIGNAL'
        self.pnl = 0
        self.pnl_percent = 0
        self.status = 'OPEN'  # 'OPEN', 'CLOSED'
    
    def close(self, exit_time, exit_price, exit_reason):
        """Close the trade"""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        self.status = 'CLOSED'
        
        # Calculate P&L
        if self.side == 'LONG':
            self.pnl_percent = ((exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            self.pnl_percent = ((self.entry_price - exit_price) / self.entry_price) * 100
        
        self.pnl = self.pnl_percent  # Simplified for percentage-based
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'entry_time': str(self.entry_time),
            'entry_price': self.entry_price,
            'side': self.side,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'exit_time': str(self.exit_time) if self.exit_time else None,
            'exit_price': self.exit_price,
            'exit_reason': self.exit_reason,
            'pnl': round(self.pnl, 2),
            'pnl_percent': round(self.pnl_percent, 2),
            'status': self.status,
            'strategy': self.strategy
        }


class Backtester:
    """Backtesting engine"""
    
    def __init__(self, initial_capital: float = 10000):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital in USDT
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades: List[Trade] = []
        self.equity_curve = []
        
    def get_historical_data(
        self,
        symbol: str,
        interval: str,
        days_back: int = 30
    ) -> pd.DataFrame:
        """
        Get historical data from Binance
        
        Args:
            symbol: Trading symbol
            interval: Candle interval
            days_back: Number of days to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            client = BinanceFuturesClient(
                config.BINANCE_API_KEY,
                config.BINANCE_API_SECRET,
                config.BINANCE_TESTNET
            )
            
            # Calculate limit based on interval
            interval_minutes = {
                '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '2h': 120, '4h': 240, '6h': 360, '12h': 720, '1d': 1440
            }
            
            minutes = interval_minutes.get(interval, 15)
            limit = min(int((days_back * 24 * 60) / minutes), 1500)
            
            klines = client.get_klines(symbol, interval, limit)
            
            if not klines:
                log.error(f"No data received for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            log.info(f"Loaded {len(df)} candles for {symbol} ({interval})")
            return df
            
        except Exception as e:
            log.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def check_stop_loss_take_profit(
        self,
        trade: Trade,
        current_time,
        high: float,
        low: float,
        close: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if SL or TP was hit
        
        Returns:
            (should_close, exit_reason)
        """
        if trade.side == 'LONG':
            # Check stop loss
            if low <= trade.stop_loss:
                return True, 'SL', trade.stop_loss
            
            # Check take profit
            if high >= trade.take_profit:
                return True, 'TP', trade.take_profit
        
        else:  # SHORT
            # Check stop loss
            if high >= trade.stop_loss:
                return True, 'SL', trade.stop_loss
            
            # Check take profit
            if low <= trade.take_profit:
                return True, 'TP', trade.take_profit
        
        return False, None, None
    
    def run_backtest(
        self,
        symbol: str,
        strategy_name: str,
        interval: str = '15m',
        days_back: int = 30,
        position_size_pct: float = 10.0,
        stop_loss_pct: float = 2.0,
        take_profit_pct: float = 4.0,
        min_signal_strength: float = 50.0
    ) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            symbol: Trading symbol
            strategy_name: Strategy to test
            interval: Candle interval
            days_back: Days of history to test
            position_size_pct: Percentage of capital per trade
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
            min_signal_strength: Minimum signal strength required
            
        Returns:
            Backtest results dictionary
        """
        log.info(f"Starting backtest: {symbol} | {strategy_name} | {interval}")
        log.info(f"Period: {days_back} days | Position size: {position_size_pct}%")
        
        # Reset state
        self.capital = self.initial_capital
        self.trades = []
        self.equity_curve = [(datetime.now(), self.initial_capital)]
        
        # Get historical data
        df = self.get_historical_data(symbol, interval, days_back)
        
        if df.empty:
            return {'error': 'No historical data available'}
        
        # Get strategy
        strategy = get_strategy(strategy_name)
        if not strategy:
            return {'error': f'Strategy {strategy_name} not found'}
        
        # Track open trade
        open_trade = None
        
        # Iterate through data
        for i in range(100, len(df)):  # Start after enough data for indicators
            current_data = df.iloc[:i+1]
            current_time = current_data.iloc[-1]['timestamp']
            current_price = current_data.iloc[-1]['close']
            current_high = current_data.iloc[-1]['high']
            current_low = current_data.iloc[-1]['low']
            
            # Check if we have an open trade
            if open_trade:
                # Check SL/TP
                should_close, exit_reason, exit_price = self.check_stop_loss_take_profit(
                    open_trade, current_time, current_high, current_low, current_price
                )
                
                if should_close:
                    open_trade.close(current_time, exit_price, exit_reason)
                    self.capital += (open_trade.pnl_percent / 100) * (self.capital * position_size_pct / 100) * config.DEFAULT_LEVERAGE
                    self.trades.append(open_trade)
                    self.equity_curve.append((current_time, self.capital))
                    open_trade = None
                    continue
            
            # Look for new signal
            if not open_trade:
                try:
                    # Generate signal
                    signal_result = strategy.analyze(current_data, symbol)
                    
                    if signal_result and signal_result.get('signal'):
                        signal = signal_result['signal']
                        strength = signal_result.get('strength', 0)
                        
                        # Check if signal meets minimum strength
                        if strength >= min_signal_strength:
                            # Calculate position size
                            position_value = self.capital * (position_size_pct / 100)
                            
                            # Calculate SL/TP
                            stop_loss, take_profit = calculate_stop_loss_take_profit(
                                current_price,
                                signal,
                                stop_loss_pct,
                                take_profit_pct
                            )
                            
                            # Create trade
                            open_trade = Trade(
                                entry_time=current_time,
                                entry_price=current_price,
                                side=signal,
                                quantity=position_value / current_price,
                                stop_loss=stop_loss,
                                take_profit=take_profit,
                                strategy=strategy_name
                            )
                            
                            log.debug(f"Signal: {signal} @ {current_price} (Strength: {strength}%)")
                
                except Exception as e:
                    log.error(f"Error analyzing candle {i}: {e}")
                    continue
        
        # Close any remaining open trade
        if open_trade:
            open_trade.close(df.iloc[-1]['timestamp'], df.iloc[-1]['close'], 'END')
            self.capital += (open_trade.pnl_percent / 100) * (self.capital * position_size_pct / 100) * config.DEFAULT_LEVERAGE
            self.trades.append(open_trade)
            self.equity_curve.append((df.iloc[-1]['timestamp'], self.capital))
        
        # Calculate statistics
        results = self.calculate_statistics(symbol, strategy_name, interval, days_back)
        
        return results
    
    def calculate_statistics(
        self,
        symbol: str,
        strategy: str,
        interval: str,
        days_back: int
    ) -> Dict:
        """Calculate backtest statistics"""
        
        if not self.trades:
            return {
                'error': 'No trades executed',
                'symbol': symbol,
                'strategy': strategy,
                'interval': interval
            }
        
        # Basic stats
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        # P&L
        total_pnl = sum(t.pnl for t in self.trades)
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        # Risk metrics
        profit_factor = abs(sum(t.pnl for t in winning_trades) / sum(t.pnl for t in losing_trades)) if losing_trades else float('inf')
        
        # Returns
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        # Max drawdown
        peak = self.initial_capital
        max_dd = 0
        for _, equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd = ((peak - equity) / peak) * 100
            if dd > max_dd:
                max_dd = dd
        
        # Trade breakdown
        long_trades = [t for t in self.trades if t.side == 'LONG']
        short_trades = [t for t in self.trades if t.side == 'SHORT']
        
        # Exit reasons
        sl_exits = len([t for t in self.trades if t.exit_reason == 'SL'])
        tp_exits = len([t for t in self.trades if t.exit_reason == 'TP'])
        
        results = {
            'symbol': symbol,
            'strategy': strategy,
            'interval': interval,
            'period_days': days_back,
            'initial_capital': self.initial_capital,
            'final_capital': round(self.capital, 2),
            'total_return_pct': round(total_return, 2),
            'total_pnl': round(total_pnl, 2),
            'total_trades': total_trades,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'win_rate_pct': round(win_rate, 2),
            'avg_win_pct': round(avg_win, 2),
            'avg_loss_pct': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown_pct': round(max_dd, 2),
            'long_trades': len(long_trades),
            'short_trades': len(short_trades),
            'tp_exits': tp_exits,
            'sl_exits': sl_exits,
            'trades': [t.to_dict() for t in self.trades[-10:]]  # Last 10 trades
        }
        
        return results
    
    def print_results(self, results: Dict):
        """Print backtest results in a formatted way"""
        
        if 'error' in results:
            log.error(f"Backtest Error: {results['error']}")
            return
        
        print("\n" + "="*70)
        print(f"  BACKTEST RESULTS - {results['strategy']}")
        print("="*70)
        
        # Overview
        print(f"\n📊 OVERVIEW:")
        print(f"  Symbol: {results['symbol']}")
        print(f"  Strategy: {results['strategy']}")
        print(f"  Interval: {results['interval']}")
        print(f"  Period: {results['period_days']} days")
        
        # Performance
        print(f"\n💰 PERFORMANCE:")
        print(f"  Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"  Final Capital:   ${results['final_capital']:,.2f}")
        
        return_color = '\033[92m' if results['total_return_pct'] > 0 else '\033[91m'
        print(f"  Total Return:    {return_color}{results['total_return_pct']:+.2f}%\033[0m")
        
        # Trades
        print(f"\n📈 TRADES:")
        print(f"  Total Trades: {results['total_trades']}")
        print(f"  Winning: {results['winning_trades']} ({results['win_rate_pct']:.1f}%)")
        print(f"  Losing:  {results['losing_trades']} ({100-results['win_rate_pct']:.1f}%)")
        print(f"  Long:  {results['long_trades']}")
        print(f"  Short: {results['short_trades']}")
        
        # Exits
        print(f"\n🎯 EXIT REASONS:")
        print(f"  Take Profit: {results['tp_exits']}")
        print(f"  Stop Loss:   {results['sl_exits']}")
        
        # Stats
        print(f"\n📊 STATISTICS:")
        print(f"  Avg Win:  {results['avg_win_pct']:+.2f}%")
        print(f"  Avg Loss: {results['avg_loss_pct']:+.2f}%")
        print(f"  Profit Factor: {results['profit_factor']:.2f}")
        print(f"  Max Drawdown:  {results['max_drawdown_pct']:.2f}%")
        
        # Last trades
        if results['trades']:
            print(f"\n📝 LAST {min(len(results['trades']), 10)} TRADES:")
            trade_data = []
            for t in results['trades']:
                pnl_color = '🟢' if t['pnl'] > 0 else '🔴'
                trade_data.append([
                    t['entry_time'][:16],
                    t['side'],
                    f"${t['entry_price']:.2f}",
                    f"${t['exit_price']:.2f}" if t['exit_price'] else "OPEN",
                    t['exit_reason'] or "-",
                    f"{pnl_color} {t['pnl_percent']:+.2f}%"
                ])
            
            print(tabulate(
                trade_data,
                headers=['Time', 'Side', 'Entry', 'Exit', 'Reason', 'P&L'],
                tablefmt='simple'
            ))
        
        print("\n" + "="*70 + "\n")
    
    def save_results(self, results: Dict, filename: str = None):
        """Save results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtest_results_{timestamp}.json"
        
        filepath = f"trading_data/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        log.info(f"Results saved to {filepath}")
        return filepath


def run_backtest_cli():
    """Run backtest from command line"""
    print("\n" + "="*70)
    print("  🤖 ATHENA BOT - BACKTESTING ENGINE")
    print("="*70 + "\n")
    
    # Get parameters
    symbol = input("Symbol (e.g., BTCUSDT) [BTCUSDT]: ").strip().upper() or 'BTCUSDT'
    
    print("\nAvailable Strategies:")
    for i, s in enumerate(config.AVAILABLE_STRATEGIES, 1):
        print(f"  {i}. {s}")
    
    strategy_idx = input(f"\nSelect strategy (1-{len(config.AVAILABLE_STRATEGIES)}) [1]: ").strip() or '1'
    strategy = config.AVAILABLE_STRATEGIES[int(strategy_idx) - 1]
    
    interval = input("Interval (1m, 5m, 15m, 1h, 4h, 1d) [15m]: ").strip() or '15m'
    days = input("Days back [30]: ").strip() or '30'
    
    print("\n🔄 Running backtest...\n")
    
    # Create backtester
    backtester = Backtester(initial_capital=10000)
    
    # Run backtest
    results = backtester.run_backtest(
        symbol=symbol,
        strategy_name=strategy,
        interval=interval,
        days_back=int(days),
        position_size_pct=10.0,
        stop_loss_pct=2.0,
        take_profit_pct=4.0,
        min_signal_strength=50.0
    )
    
    # Print results
    backtester.print_results(results)
    
    # Save
    save = input("Save results to file? (y/n) [y]: ").strip().lower() or 'y'
    if save == 'y':
        filepath = backtester.save_results(results)
        print(f"✅ Results saved to {filepath}")


if __name__ == "__main__":
    run_backtest_cli()
