"""
Batch Backtesting - Test multiple strategies/symbols at once
"""
import sys
from datetime import datetime
from backtest import Backtester
from logger import get_logger
import config

log = get_logger('BatchBacktest')


def run_batch_backtest():
    """Run backtests on multiple strategies"""
    
    print("\n" + "="*80)
    print("  🤖 ATHENA BOT - BATCH BACKTESTING")
    print("="*80 + "\n")
    
    # Test parameters
    symbols = ['BTCUSDT', 'ETHUSDT']
    strategies = ['EMA_CROSS', 'MACD_SIGNAL', 'RSI_DIVERGENCE', 'TRIPLE_EMA']
    interval = '15m'
    days_back = 30
    
    print(f"Testing Configuration:")
    print(f"  Symbols: {', '.join(symbols)}")
    print(f"  Strategies: {', '.join(strategies)}")
    print(f"  Interval: {interval}")
    print(f"  Period: {days_back} days")
    print(f"  Initial Capital: $10,000")
    print(f"  Position Size: 10% per trade")
    print(f"  Stop Loss: 2%")
    print(f"  Take Profit: 4%")
    print(f"  Min Signal Strength: 50%")
    print("\n" + "="*80 + "\n")
    
    all_results = []
    
    # Run backtests
    for symbol in symbols:
        for strategy in strategies:
            print(f"\n{'='*80}")
            print(f"Testing {strategy} on {symbol}...")
            print('='*80 + "\n")
            
            try:
                backtester = Backtester(initial_capital=10000)
                
                results = backtester.run_backtest(
                    symbol=symbol,
                    strategy_name=strategy,
                    interval=interval,
                    days_back=days_back,
                    position_size_pct=10.0,
                    stop_loss_pct=2.0,
                    take_profit_pct=4.0,
                    min_signal_strength=50.0
                )
                
                if 'error' not in results:
                    backtester.print_results(results)
                    all_results.append(results)
                else:
                    print(f"❌ Error: {results['error']}\n")
                
            except Exception as e:
                log.error(f"Error testing {strategy} on {symbol}: {e}")
                print(f"❌ Error: {e}\n")
    
    # Summary
    if all_results:
        print("\n" + "="*80)
        print("  📊 SUMMARY - ALL STRATEGIES")
        print("="*80 + "\n")
        
        # Sort by total return
        all_results.sort(key=lambda x: x['total_return_pct'], reverse=True)
        
        print(f"{'Rank':<6} {'Symbol':<10} {'Strategy':<20} {'Return':<12} {'Win Rate':<12} {'Trades':<8}")
        print("-" * 80)
        
        for i, r in enumerate(all_results, 1):
            return_str = f"{r['total_return_pct']:+.2f}%"
            return_color = '\033[92m' if r['total_return_pct'] > 0 else '\033[91m'
            
            print(f"{i:<6} {r['symbol']:<10} {r['strategy']:<20} {return_color}{return_str:<12}\033[0m {r['win_rate_pct']:.1f}%{'':<8} {r['total_trades']:<8}")
        
        # Best performers
        print("\n🏆 BEST PERFORMERS:\n")
        for i, r in enumerate(all_results[:3], 1):
            print(f"{i}. {r['strategy']} on {r['symbol']}: {r['total_return_pct']:+.2f}% ({r['total_trades']} trades)")
        
        # Average stats
        avg_return = sum(r['total_return_pct'] for r in all_results) / len(all_results)
        avg_win_rate = sum(r['win_rate_pct'] for r in all_results) / len(all_results)
        total_trades = sum(r['total_trades'] for r in all_results)
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"  Average Return: {avg_return:+.2f}%")
        print(f"  Average Win Rate: {avg_win_rate:.1f}%")
        print(f"  Total Trades: {total_trades}")
        
        # Save combined results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"batch_backtest_{timestamp}.json"
        
        import json
        with open(f"trading_data/{filename}", 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n✅ Full results saved to trading_data/{filename}")
    
    print("\n" + "="*80 + "\n")


def run_quick_test():
    """Quick test of best strategy"""
    print("\n" + "="*80)
    print("  ⚡ QUICK BACKTEST - EMA CROSS on BTCUSDT")
    print("="*80 + "\n")
    
    backtester = Backtester(initial_capital=10000)
    
    results = backtester.run_backtest(
        symbol='BTCUSDT',
        strategy_name='EMA_CROSS',
        interval='15m',
        days_back=30,
        position_size_pct=10.0,
        stop_loss_pct=2.0,
        take_profit_pct=4.0,
        min_signal_strength=50.0
    )
    
    backtester.print_results(results)
    
    if 'error' not in results:
        print(f"✅ Test completed successfully!")
        print(f"   Return: {results['total_return_pct']:+.2f}%")
        print(f"   Win Rate: {results['win_rate_pct']:.1f}%")
        print(f"   Total Trades: {results['total_trades']}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import os
    os.makedirs('trading_data', exist_ok=True)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        run_quick_test()
    else:
        run_batch_backtest()
