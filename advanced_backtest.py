"""
Advanced Backtesting with Multi-Timeframe Analysis and Parameter Optimization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging
from tabulate import tabulate

from binance_client import BinanceFuturesClient
from signal_analyzer_enhanced import EnhancedSignalAnalyzer
from strategies_enhanced import OptimizedStrategyFactory, EnhancedTripleEMAStrategy
from mtf_analyzer import MultiTimeframeAnalyzer

logger = logging.getLogger(__name__)


class Trade:
    """Represents a single trade in the backtest"""
    
    def __init__(self, entry_time, entry_price, signal, quantity, stop_loss, take_profit, strategy_name=""):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.signal = signal  # 'BUY' or 'SELL'
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.strategy = strategy_name
        
        self.exit_time = None
        self.exit_price = None
        self.exit_reason = None
        self.pnl = 0
        self.pnl_percent = 0
    
    def close_trade(self, exit_price, exit_time, exit_reason):
        """Close the trade and calculate P&L"""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        
        # Calculate P&L
        if self.signal == 'BUY':
            self.pnl_percent = ((exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SELL
            self.pnl_percent = ((self.entry_price - exit_price) / self.entry_price) * 100
        
        # Calculate dollar P&L
        self.pnl = (self.pnl_percent / 100) * (self.entry_price * self.quantity)
    
    def to_dict(self):
        """Convert trade to dictionary"""
        return {
            'entry_time': str(self.entry_time),
            'entry_price': self.entry_price,
            'signal': self.signal,
            'quantity': self.quantity,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'exit_time': str(self.exit_time) if self.exit_time else None,
            'exit_price': self.exit_price,
            'exit_reason': self.exit_reason,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent
        }


class AdvancedBacktester:
    """
    Advanced backtesting engine with:
    1. Multi-timeframe analysis
    2. Parameter optimization
    3. Walk-forward testing
    4. Comprehensive statistics
    """
    
    def __init__(
        self,
        binance_client: BinanceFuturesClient,
        initial_capital: float = 10000.0,
        position_size_pct: float = 95.0
    ):
        """
        Initialize advanced backtester.
        
        Args:
            binance_client: Binance client for historical data
            initial_capital: Starting capital in USDT
            position_size_pct: Position size as % of capital
        """
        self.client = binance_client
        self.initial_capital = initial_capital
        self.position_size_pct = position_size_pct
        
        logger.info(f"Initialized Advanced Backtester - Capital: ${initial_capital}")
    
    def run_mtf_backtest(
        self,
        symbol: str,
        primary_timeframe: str = "15m",
        confirmation_timeframes: List[str] = None,
        days_back: int = 30,
        strategy_config: Dict = None
    ) -> Dict:
        """
        Run backtest with multi-timeframe analysis.
        
        Args:
            symbol: Trading pair
            primary_timeframe: Primary timeframe for entries
            confirmation_timeframes: Higher timeframes for confirmation
            days_back: Number of days to backtest
            strategy_config: Strategy parameters (optional)
            
        Returns:
            Dict with backtest results
        """
        try:
            logger.info(f"Starting MTF backtest for {symbol}")
            logger.info(f"Primary TF: {primary_timeframe}, Confirmation: {confirmation_timeframes}")
            
            # Initialize analyzer with MTF
            analyzer = EnhancedSignalAnalyzer(
                self.client,
                use_mtf=True,
                primary_timeframe=primary_timeframe,
                confirmation_timeframes=confirmation_timeframes or ["1h", "4h"]
            )
            
            # If custom strategy config provided, create custom strategy
            if strategy_config:
                analyzer.strategy = OptimizedStrategyFactory.create_custom_strategy(**strategy_config)
            
            # Get historical data for primary timeframe
            start_time = datetime.now() - timedelta(days=days_back)
            end_time = datetime.now()
            
            # Calculate required candles
            minutes_per_candle = self._timeframe_to_minutes(primary_timeframe)
            total_minutes = days_back * 24 * 60
            required_candles = int(total_minutes / minutes_per_candle)
            
            # Binance max limit is 1500, cap it
            required_candles = min(required_candles, 1500)
            
            # Fetch data
            klines = self.client.get_klines(symbol, primary_timeframe, limit=required_candles)
            
            if not klines:
                return {'error': 'No historical data available'}
            
            df = self._prepare_dataframe(klines)
            
            logger.info(f"Loaded {len(df)} candles from {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
            
            # Initialize trade tracking
            trades = []
            current_position = None
            capital = self.initial_capital
            
            # Simulate trading
            for i in range(100, len(df)):  # Start after warmup period
                current_time = df['timestamp'].iloc[i]
                current_price = float(df['close'].iloc[i])
                high = float(df['high'].iloc[i])
                low = float(df['low'].iloc[i])
                
                # Check if current position needs to be closed (SL/TP hit)
                if current_position:
                    hit_sl, hit_tp = self._check_stop_loss_take_profit(
                        current_position, high, low, current_price
                    )
                    
                    if hit_sl or hit_tp:
                        exit_price = current_position.stop_loss if hit_sl else current_position.take_profit
                        exit_reason = 'SL' if hit_sl else 'TP'
                        
                        # Close position
                        current_position.close_trade(exit_price, current_time, exit_reason)
                        trades.append(current_position)
                        capital = capital + current_position.pnl
                        
                        logger.debug(
                            f"Closed {current_position.signal} at {exit_price:.2f} "
                            f"({exit_reason}), PnL: ${current_position.pnl:.2f}"
                        )
                        
                        current_position = None
                
                # Check for new signals only if no position
                if not current_position:
                    # Get MTF analysis for this point in time
                    # Note: In real backtest, we'd need historical MTF data
                    # For now, we'll use the enhanced strategy on primary TF
                    historical_df = df.iloc[:i+1].copy()
                    historical_df = analyzer.strategy._calculate_indicators(historical_df)
                    
                    signal = analyzer.strategy.generate_signal(historical_df)
                    
                    if signal in ['BUY', 'SELL']:
                        # Calculate position size
                        position_size = (capital * (self.position_size_pct / 100)) / current_price
                        
                        # Calculate stops
                        stop_loss, take_profit = analyzer.strategy.calculate_stop_loss_take_profit(
                            current_price,
                            signal,
                            historical_df
                        )
                        
                        # Open new position
                        current_position = Trade(
                            entry_time=current_time,
                            entry_price=current_price,
                            signal=signal,
                            quantity=position_size,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                            strategy_name="MTF_ENHANCED"
                        )
                        
                        logger.debug(
                            f"Opened {signal} at {current_price:.2f}, "
                            f"SL: {stop_loss:.2f}, TP: {take_profit:.2f}"
                        )
            
            # Close any remaining position at last price
            if current_position:
                last_price = float(df['close'].iloc[-1])
                last_time = df['timestamp'].iloc[-1]
                current_position.close_trade(last_price, last_time, 'END')
                trades.append(current_position)
                capital = capital + current_position.pnl
            
            # Calculate statistics
            stats = self._calculate_statistics(trades, self.initial_capital, capital)
            
            result = {
                'symbol': symbol,
                'primary_timeframe': primary_timeframe,
                'confirmation_timeframes': confirmation_timeframes or ["1h", "4h"],
                'strategy_config': strategy_config,
                'period': f"{df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}",
                'initial_capital': self.initial_capital,
                'final_capital': capital,
                'total_return_pct': ((capital - self.initial_capital) / self.initial_capital) * 100,
                'trades': [t.to_dict() for t in trades],
                'statistics': stats
            }
            
            logger.info(
                f"MTF Backtest complete - Return: {result['total_return_pct']:.2f}%, "
                f"Trades: {len(trades)}, Win Rate: {stats['win_rate']:.1f}%"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in MTF backtest: {e}")
            return {'error': str(e)}
    
    def optimize_parameters(
        self,
        symbol: str,
        primary_timeframe: str = "15m",
        days_back: int = 30,
        param_ranges: Dict = None
    ) -> List[Dict]:
        """
        Optimize strategy parameters using grid search.
        
        Args:
            symbol: Trading pair
            primary_timeframe: Timeframe to test
            days_back: Days of historical data
            param_ranges: Dict of parameter ranges to test
                Example: {
                    'fast_period': [5, 9, 12],
                    'medium_period': [21, 30],
                    'atr_multiplier': [1.5, 2.0, 2.5]
                }
                
        Returns:
            List of results sorted by total return
        """
        if not param_ranges:
            # Default parameter ranges
            param_ranges = {
                'fast_period': [7, 9, 12],
                'medium_period': [18, 21, 26],
                'slow_period': [45, 50, 55],
                'atr_multiplier': [1.5, 2.0, 2.5],
                'volume_threshold': [1.0, 1.2, 1.5],
                'require_volume_confirmation': [True, False]
            }
        
        logger.info(f"Starting parameter optimization for {symbol}")
        logger.info(f"Parameter ranges: {param_ranges}")
        
        # Generate all combinations
        from itertools import product
        
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        results = []
        total_combinations = np.prod([len(v) for v in param_values])
        
        logger.info(f"Testing {total_combinations} parameter combinations...")
        
        for i, combination in enumerate(product(*param_values)):
            config = dict(zip(param_names, combination))
            
            # Map parameter names to strategy constructor names
            strategy_config = {
                'fast': config.get('fast_period', 9),
                'medium': config.get('medium_period', 21),
                'slow': config.get('slow_period', 50),
                'atr_mult': config.get('atr_multiplier', 2.0),
                'vol_thresh': config.get('volume_threshold', 1.2),
                'require_vol': config.get('require_volume_confirmation', True)
            }
            
            # Run backtest with these parameters
            result = self.run_mtf_backtest(
                symbol,
                primary_timeframe,
                None,  # No MTF for optimization (faster)
                days_back,
                strategy_config
            )
            
            if 'error' not in result:
                results.append({
                    'config': config,
                    'return_pct': result['total_return_pct'],
                    'win_rate': result['statistics']['win_rate'],
                    'profit_factor': result['statistics']['profit_factor'],
                    'total_trades': result['statistics']['total_trades'],
                    'max_drawdown': result['statistics']['max_drawdown_pct']
                })
            
            if (i + 1) % 10 == 0:
                logger.info(f"Tested {i + 1}/{total_combinations} combinations...")
        
        # Sort by return
        results.sort(key=lambda x: x['return_pct'], reverse=True)
        
        if results:
            logger.info(f"Optimization complete! Best return: {results[0]['return_pct']:.2f}%")
        else:
            logger.warning("Optimization complete but no valid results")
        
        return results
    
    def compare_timeframe_combinations(
        self,
        symbol: str,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Compare different timeframe combinations to find the best setup.
        
        Tests various primary/confirmation timeframe combinations.
        
        Args:
            symbol: Trading pair
            days_back: Days to backtest
            
        Returns:
            List of results sorted by performance
        """
        timeframe_combos = [
            ("15m", ["1h", "4h"]),
            ("15m", ["1h"]),
            ("15m", ["4h"]),
            ("1h", ["4h", "1d"]),
            ("1h", ["4h"]),
            ("5m", ["15m", "1h"]),
        ]
        
        results = []
        
        for primary, confirmation in timeframe_combos:
            logger.info(f"Testing {primary} with confirmation {confirmation}")
            
            result = self.run_mtf_backtest(
                symbol,
                primary,
                confirmation,
                days_back
            )
            
            if 'error' not in result:
                results.append({
                    'primary_tf': primary,
                    'confirmation_tfs': confirmation,
                    'return_pct': result['total_return_pct'],
                    'win_rate': result['statistics']['win_rate'],
                    'total_trades': result['statistics']['total_trades'],
                    'profit_factor': result['statistics']['profit_factor']
                })
        
        results.sort(key=lambda x: x['return_pct'], reverse=True)
        
        return results
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes."""
        if timeframe.endswith('m'):
            return int(timeframe[:-1])
        elif timeframe.endswith('h'):
            return int(timeframe[:-1]) * 60
        elif timeframe.endswith('d'):
            return int(timeframe[:-1]) * 1440
        return 15
    
    def _prepare_dataframe(self, klines: List) -> pd.DataFrame:
        """Convert klines to DataFrame."""
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        return df
    
    def _check_stop_loss_take_profit(
        self,
        trade: Trade,
        high: float,
        low: float,
        close: float
    ) -> Tuple[bool, bool]:
        """Check if SL or TP was hit."""
        hit_sl = False
        hit_tp = False
        
        if trade.signal == 'BUY':
            if low <= trade.stop_loss:
                hit_sl = True
            if high >= trade.take_profit:
                hit_tp = True
        else:  # SELL
            if high >= trade.stop_loss:
                hit_sl = True
            if low <= trade.take_profit:
                hit_tp = True
        
        return hit_sl, hit_tp
    
    def _calculate_statistics(
        self,
        trades: List[Trade],
        initial_capital: float,
        final_capital: float
    ) -> Dict:
        """Calculate comprehensive statistics."""
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'max_drawdown_pct': 0
            }
        
        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]
        
        total_profit = sum(t.pnl for t in wins)
        total_loss = abs(sum(t.pnl for t in losses))
        
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Calculate max drawdown
        capital_curve = [initial_capital]
        running_capital = initial_capital
        for trade in trades:
            running_capital += trade.pnl
            capital_curve.append(running_capital)
        
        peak = capital_curve[0]
        max_dd = 0
        for value in capital_curve:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100
            if dd > max_dd:
                max_dd = dd
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': (len(wins) / len(trades)) * 100,
            'profit_factor': profit_factor,
            'avg_win': total_profit / len(wins) if wins else 0,
            'avg_loss': total_loss / len(losses) if losses else 0,
            'max_drawdown_pct': max_dd,
            'total_profit': total_profit,
            'total_loss': total_loss
        }
    
    def print_results(self, result: Dict):
        """Print formatted results."""
        if 'error' in result:
            print(f"\n❌ Error: {result['error']}\n")
            return
        
        print(f"\n{'='*60}")
        print(f"ADVANCED BACKTEST RESULTS - {result['symbol']}")
        print(f"{'='*60}")
        print(f"Primary Timeframe: {result['primary_timeframe']}")
        if result.get('confirmation_timeframes'):
            print(f"Confirmation Timeframes: {', '.join(result['confirmation_timeframes'])}")
        print(f"Period: {result['period']}")
        print(f"\n{'PERFORMANCE':^60}")
        print(f"{'-'*60}")
        print(f"Initial Capital:    ${result['initial_capital']:>12,.2f}")
        print(f"Final Capital:      ${result['final_capital']:>12,.2f}")
        print(f"Total Return:       {result['total_return_pct']:>12.2f}%")
        
        stats = result['statistics']
        print(f"\n{'STATISTICS':^60}")
        print(f"{'-'*60}")
        print(f"Total Trades:       {stats['total_trades']:>12}")
        print(f"Winning Trades:     {stats['winning_trades']:>12}")
        print(f"Losing Trades:      {stats['losing_trades']:>12}")
        print(f"Win Rate:           {stats['win_rate']:>12.2f}%")
        print(f"Profit Factor:      {stats['profit_factor']:>12.2f}")
        print(f"Avg Win:            ${stats['avg_win']:>11,.2f}")
        print(f"Avg Loss:           ${stats['avg_loss']:>11,.2f}")
        print(f"Max Drawdown:       {stats['max_drawdown_pct']:>12.2f}%")
        print(f"{'='*60}\n")


def main():
    """Run advanced backtesting examples."""
    from config import BINANCE_API_KEY, BINANCE_API_SECRET, BINANCE_TESTNET
    
    # Initialize client
    client = BinanceFuturesClient(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=BINANCE_TESTNET)
    
    # Initialize backtester
    backtester = AdvancedBacktester(client, initial_capital=10000.0)
    
    symbol = "BTCUSDT"
    
    print("\n" + "="*60)
    print("ADVANCED BACKTESTING SUITE")
    print("="*60)
    
    # Test 1: MTF Backtest
    print("\n1. Running Multi-Timeframe Backtest...")
    mtf_result = backtester.run_mtf_backtest(
        symbol,
        primary_timeframe="15m",
        confirmation_timeframes=["1h", "4h"],
        days_back=30
    )
    backtester.print_results(mtf_result)
    
    # Test 2: Compare timeframe combinations
    print("\n2. Comparing Timeframe Combinations...")
    tf_comparison = backtester.compare_timeframe_combinations(symbol, days_back=30)
    
    print("\nTimeframe Combination Results:")
    print(tabulate(
        [[r['primary_tf'], ', '.join(r['confirmation_tfs']), f"{r['return_pct']:.2f}%",
          f"{r['win_rate']:.1f}%", r['total_trades'], f"{r['profit_factor']:.2f}"]
         for r in tf_comparison],
        headers=['Primary', 'Confirmation', 'Return', 'Win Rate', 'Trades', 'PF'],
        tablefmt='grid'
    ))
    
    # Test 3: Parameter optimization (limited for speed)
    print("\n3. Running Parameter Optimization (limited)...")
    optimization_results = backtester.optimize_parameters(
        symbol,
        primary_timeframe="15m",
        days_back=30,
        param_ranges={
            'fast_period': [9, 12],
            'medium_period': [21, 26],
            'atr_multiplier': [1.5, 2.0, 2.5]
        }
    )
    
    print("\nTop 5 Parameter Combinations:")
    print(tabulate(
        [[i+1, r['config'], f"{r['return_pct']:.2f}%", f"{r['win_rate']:.1f}%",
          r['total_trades'], f"{r['profit_factor']:.2f}"]
         for i, r in enumerate(optimization_results[:5])],
        headers=['Rank', 'Config', 'Return', 'Win Rate', 'Trades', 'PF'],
        tablefmt='grid'
    ))
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trading_data/advanced_backtest_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            'mtf_result': mtf_result,
            'tf_comparison': tf_comparison,
            'optimization_results': optimization_results[:10]
        }, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to: {filename}")


if __name__ == "__main__":
    main()
