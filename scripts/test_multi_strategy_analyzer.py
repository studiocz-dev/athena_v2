"""
Test Multi-Strategy Analyzer with Discord Message Formatting
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from binance_client import BinanceFuturesClient
from multi_strategy_analyzer import MultiStrategySignalAnalyzer
import config

print("=" * 70)
print("TESTING MULTI-STRATEGY ANALYZER")
print("=" * 70)

# Initialize Binance client
print("\n1. Initializing Binance testnet client...")
client = BinanceFuturesClient(
    api_key=config.BINANCE_API_KEY,
    api_secret=config.BINANCE_API_SECRET,
    testnet=True
)
print("✅ Client initialized")

# Initialize multi-strategy analyzer
print("\n2. Initializing Multi-Strategy Analyzer...")
analyzer = MultiStrategySignalAnalyzer(client, primary_timeframe='15m')
print("✅ Analyzer ready with all 8 strategies")

# Test with BTC
print("\n3. Analyzing BTCUSDT...")
print("-" * 70)
result = analyzer.analyze_symbol('BTCUSDT')

if 'error' in result:
    print(f"❌ Error: {result['error']}")
else:
    print(f"\n✅ Analysis Complete!")
    print(f"\nSymbol: {result['symbol']}")
    print(f"Signal: {result['final_signal']}")
    print(f"Strength: {result['signal_strength']}")
    print(f"Confidence: {result['confidence']:.1f}%")
    print(f"Consensus: {result['consensus']:.1f}%")
    print(f"Stars: {'⭐' * result['stars']}")
    print(f"Price: ${result['current_price']:,.2f}")
    print(f"RSI: {result['rsi']:.1f}")
    
    if result['final_signal'] != 'HOLD':
        print(f"\nEntry Levels:")
        print(f"  Stop Loss: ${result['stop_loss']:,.2f}")
        print(f"  Take Profit: ${result['take_profit']:,.2f}")
        print(f"  Risk/Reward: {result['risk_reward']:.2f}:1")
    
    print(f"\nStrategy Breakdown:")
    for strategy, data in result['strategy_signals'].items():
        emoji = '🟢' if data['signal'] == 'BUY' else ('🔴' if data['signal'] == 'SELL' else '⚪')
        print(f"  {emoji} {strategy:20} {data['signal']:4} ({data['strength']})")
    
    print(f"\nScoring:")
    print(f"  Buy:  {result['buy_score']:.2f}")
    print(f"  Sell: {result['sell_score']:.2f}")
    print(f"  Hold: {result['hold_score']:.2f}")
    
    print(f"\nRecommendation:")
    print(f"  {result['recommendation']}")
    
    # Test Discord message formatting
    print("\n" + "=" * 70)
    print("DISCORD MESSAGE FORMAT:")
    print("=" * 70)
    
    discord_msg = analyzer.format_discord_message(result)
    if discord_msg:
        print(discord_msg)
    else:
        print("(No message - HOLD signal)")

print("\n" + "=" * 70)
print("TEST COMPLETE!")
print("=" * 70)
