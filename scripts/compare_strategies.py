"""
Quick MTF Comparison Script
Compare single timeframe vs multi-timeframe strategies
"""

import sys
from datetime import datetime
from tabulate import tabulate
import json

from binance_client import BinanceFuturesClient
from advanced_backtest import AdvancedBacktester
from backtest import Backtester
from strategies import TripleEMAStrategy
from config import BINANCE_API_KEY, BINANCE_API_SECRET, BINANCE_TESTNET


def compare_strategies(symbol="ETHUSDT", days=30):
    """Compare baseline vs enhanced MTF strategy."""
    
    print(f"\n{'='*80}")
    print(f"STRATEGY COMPARISON: Baseline vs Multi-Timeframe Enhanced")
    print(f"Symbol: {symbol} | Period: {days} days")
    print(f"{'='*80}\n")
    
    client = BinanceFuturesClient(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=BINANCE_TESTNET)
    
    # Test 1: Baseline (from previous batch backtest)
    print("1️⃣  Running BASELINE Strategy (Single Timeframe - 15m)...")
    baseline_backtester = Backtester(initial_capital=10000.0)
    baseline_result = baseline_backtester.run_backtest(
        symbol=symbol,
        strategy_name="TRIPLE_EMA",
        interval="15m",
        days_back=days,
        position_size_pct=95.0
    )
    
    print(f"   ✅ Baseline: {baseline_result['total_return_pct']:.2f}% return, "
          f"{baseline_result['total_trades']} trades, "
          f"{baseline_result['win_rate_pct']:.1f}% win rate\n")
    
    # Test 2: MTF Enhanced Strategy
    print("2️⃣  Running MTF ENHANCED Strategy (15m + 1h + 4h confirmation)...")
    mtf_backtester = AdvancedBacktester(client, initial_capital=10000.0)
    mtf_result = mtf_backtester.run_mtf_backtest(
        symbol=symbol,
        primary_timeframe="15m",
        confirmation_timeframes=["1h", "4h"],
        days_back=days
    )
    
    if 'error' not in mtf_result:
        print(f"   ✅ MTF Enhanced: {mtf_result['total_return_pct']:.2f}% return, "
              f"{mtf_result['statistics']['total_trades']} trades, "
              f"{mtf_result['statistics']['win_rate']:.1f}% win rate\n")
    else:
        print(f"   ❌ Error: {mtf_result['error']}\n")
        return
    
    # Test 3: Optimized Parameters
    print("3️⃣  Running OPTIMIZED Strategy (Best parameters from optimization)...")
    optimized_config = {
        'fast': 12,
        'medium': 21,
        'slow': 50,
        'atr_mult': 2.5,
        'vol_thresh': 1.2,
        'require_vol': True
    }
    
    optimized_result = mtf_backtester.run_mtf_backtest(
        symbol=symbol,
        primary_timeframe="15m",
        confirmation_timeframes=["1h", "4h"],
        days_back=days,
        strategy_config=optimized_config
    )
    
    if 'error' not in optimized_result:
        print(f"   ✅ Optimized: {optimized_result['total_return_pct']:.2f}% return, "
              f"{optimized_result['statistics']['total_trades']} trades, "
              f"{optimized_result['statistics']['win_rate']:.1f}% win rate\n")
    
    # Comparison Table
    print(f"\n{'='*80}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*80}\n")
    
    comparison_data = []
    
    # Baseline
    comparison_data.append([
        "Baseline (15m only)",
        f"{baseline_result['total_return_pct']:.2f}%",
        baseline_result['total_trades'],
        f"{baseline_result['win_rate_pct']:.1f}%",
        f"{baseline_result['profit_factor']:.2f}",
        f"{baseline_result['max_drawdown_pct']:.2f}%"
    ])
    
    # MTF Enhanced
    if 'error' not in mtf_result:
        comparison_data.append([
            "MTF Enhanced (15m+1h+4h)",
            f"{mtf_result['total_return_pct']:.2f}%",
            mtf_result['statistics']['total_trades'],
            f"{mtf_result['statistics']['win_rate']:.1f}%",
            f"{mtf_result['statistics']['profit_factor']:.2f}",
            f"{mtf_result['statistics']['max_drawdown_pct']:.2f}%"
        ])
    
    # Optimized
    if 'error' not in optimized_result:
        comparison_data.append([
            "Optimized (12/21 EMA, 2.5x ATR)",
            f"{optimized_result['total_return_pct']:.2f}%",
            optimized_result['statistics']['total_trades'],
            f"{optimized_result['statistics']['win_rate']:.1f}%",
            f"{optimized_result['statistics']['profit_factor']:.2f}",
            f"{optimized_result['statistics']['max_drawdown_pct']:.2f}%"
        ])
    
    print(tabulate(
        comparison_data,
        headers=['Strategy', 'Return', 'Trades', 'Win Rate', 'Profit Factor', 'Max DD'],
        tablefmt='grid'
    ))
    
    # Calculate improvements
    if 'error' not in mtf_result:
        baseline_return = baseline_result['total_return_pct']
        mtf_return = mtf_result['total_return_pct']
        improvement = mtf_return - baseline_return
        
        print(f"\n📊 KEY INSIGHTS:")
        print(f"   • MTF Enhanced improved returns by {improvement:+.2f} percentage points")
        print(f"   • Baseline had {baseline_result['total_trades']} trades "
              f"vs MTF's {mtf_result['statistics']['total_trades']} trades")
        
        if mtf_result['statistics']['total_trades'] < baseline_result['total_trades']:
            print(f"   • MTF filtered out {baseline_result['total_trades'] - mtf_result['statistics']['total_trades']} "
                  f"potentially bad trades (quality over quantity)")
        
        win_rate_diff = mtf_result['statistics']['win_rate'] - baseline_result['win_rate_pct']
        print(f"   • Win rate improved by {win_rate_diff:+.1f} percentage points")
        
        if 'error' not in optimized_result:
            opt_return = optimized_result['total_return_pct']
            total_improvement = opt_return - baseline_return
            print(f"   • Optimized strategy achieved {total_improvement:+.2f} percentage points improvement")
    
    print(f"\n{'='*80}")
    print("RECOMMENDATION")
    print(f"{'='*80}")
    
    if 'error' not in optimized_result and optimized_result['total_return_pct'] > baseline_result['total_return_pct']:
        print("\n✅ Use the OPTIMIZED MTF Strategy for live trading!")
        print(f"   Config: Fast EMA: 12, Medium EMA: 21, ATR Multiplier: 2.5x")
        print(f"   Expected: ~{optimized_result['total_return_pct']:.2f}% return per {days} days")
        print(f"   Win Rate: ~{optimized_result['statistics']['win_rate']:.1f}%")
    elif 'error' not in mtf_result and mtf_result['total_return_pct'] > baseline_result['total_return_pct']:
        print("\n✅ Use the MTF Enhanced Strategy for live trading!")
        print(f"   Expected: ~{mtf_result['total_return_pct']:.2f}% return per {days} days")
        print(f"   Win Rate: ~{mtf_result['statistics']['win_rate']:.1f}%")
    else:
        print("\n⚠️  Baseline strategy performed best in this test period.")
        print("   Consider testing on different timeframes or longer periods.")
    
    print(f"\n{'='*80}\n")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trading_data/strategy_comparison_{symbol}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            'symbol': symbol,
            'days': days,
            'baseline': baseline_result,
            'mtf_enhanced': mtf_result if 'error' not in mtf_result else {'error': mtf_result.get('error')},
            'optimized': optimized_result if 'error' not in optimized_result else {'error': optimized_result.get('error')}
        }, f, indent=2, default=str)
    
    print(f"💾 Results saved to: {filename}\n")


if __name__ == "__main__":
    # Get symbol from command line or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else "ETHUSDT"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    compare_strategies(symbol, days)
