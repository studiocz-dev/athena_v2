"""
🚀 DEPLOY MULTI-STRATEGY BOT IN SIGNAL-ONLY MODE
Sends all signals to Discord without executing trades
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("=" * 70)
print("🚀 ATHENA BOT - MULTI-STRATEGY DEPLOYMENT")
print("=" * 70)
print()

# Check configuration
print("📋 CHECKING CONFIGURATION...")
print("-" * 70)

import config

print(f"✅ Exchange: {config.EXCHANGE.upper()}")
print(f"✅ Trading Enabled: {config.TRADING_ENABLED}")
print(f"✅ Signal Channel: {config.SIGNAL_CHANNEL_ID}")
print(f"✅ Leverage: {config.DEFAULT_LEVERAGE}x")
print(f"✅ Position Size: ${config.DEFAULT_ORDER_SIZE_USDT}")

if config.EXCHANGE == 'bybit':
    print(f"✅ Bybit Demo: {config.BYBIT_DEMO}")
elif config.EXCHANGE == 'binance':
    print(f"✅ Binance Testnet: {config.BINANCE_TESTNET}")

print()
print("📊 MULTI-STRATEGY SYSTEM:")
print("-" * 70)
print("✅ 1. Pivot Points Strategy")
print("✅ 2. VWAP Strategy")  
print("✅ 3. Bollinger Bands Strategy")
print("✅ 4. Stoch+RSI+MACD Triple Oscillator")
print("✅ 5. Fibonacci Retracements")
print("✅ 6. Ichimoku Cloud")
print("✅ 7. Parabolic SAR")
print("✅ 8. 1-Min Scalping (optional)")
print()
print("🎯 Weighted Scoring System: ENABLED")
print("📈 Multi-Timeframe Analysis: ENABLED")
print("🔔 Discord Signals: ENABLED")
print()

# Check if trading is disabled (signal-only mode)
if not config.TRADING_ENABLED:
    print("🟢 MODE: SIGNAL-ONLY (No trades will be executed)")
    print("   → Bot will analyze markets and send signals to Discord")
    print("   → Perfect for testing and validation")
    print()
else:
    print("⚠️  MODE: LIVE TRADING")
    print("   → Bot WILL execute trades automatically")
    print("   → Make sure you're ready for this!")
    print()

print("=" * 70)
print("🚀 READY TO START!")
print("=" * 70)
print()

# Ask for confirmation
response = input("Start the bot? (yes/no): ").strip().lower()

if response in ['yes', 'y']:
    print()
    print("🚀 Starting Athena Bot...")
    print("=" * 70)
    print()
    
    # Import and run
    from auto_trader import AutoTrader
    
    try:
        bot = AutoTrader()
        bot.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n❌ Deployment cancelled")
    print("\nTo start later, run: python scripts\\deploy_bot.py")
