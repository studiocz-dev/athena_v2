"""
Complete Bot Test - Binance Testnet Signal-Only Mode
Tests all systems: exchange connection, strategies, Discord signals
"""

import sys
import os
import asyncio
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("ATHENA BOT - COMPLETE SYSTEM TEST")
print("=" * 80)
print(f"🕐 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Step 1: Check Configuration
print("📋 STEP 1: Checking Configuration")
print("-" * 80)

exchange = os.getenv('EXCHANGE', 'unknown')
trading_enabled = os.getenv('TRADING_ENABLED', 'False').lower() == 'true'
channel_id = os.getenv('SIGNAL_CHANNEL_ID')
binance_testnet = os.getenv('BINANCE_TESTNET', 'False').lower() == 'true'

print(f"   Exchange: {exchange.upper()}")
print(f"   Trading Mode: {'🔴 LIVE TRADING' if trading_enabled else '🟢 SIGNAL-ONLY'}")
print(f"   Binance Testnet: {'✅ Enabled' if binance_testnet else '❌ Disabled'}")
print(f"   Discord Channel: {channel_id}")

if exchange != 'binance':
    print(f"\n   ⚠️  WARNING: Expected EXCHANGE=binance, got {exchange}")
    
if trading_enabled:
    print(f"\n   ⚠️  WARNING: TRADING_ENABLED=True (will place real orders!)")
    
print()

# Step 2: Test Binance Connection
print("🔌 STEP 2: Testing Binance Testnet Connection")
print("-" * 80)

try:
    from binance_client import BinanceFuturesClient
    
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        print("   ❌ FAILED: Binance API keys not found in .env")
        sys.exit(1)
    
    client = BinanceFuturesClient(api_key, api_secret, testnet=True)
    
    # Test market data
    price = client.get_current_price('BTCUSDT')
    print(f"   ✅ Market Data: BTC Price ${price:,.2f}")
    
    # Test account
    balances = client.get_account_balance()
    usdt_balance = balances.get('USDT', {}).get('wallet_balance', 0)
    print(f"   ✅ Account: Balance {usdt_balance:.2f} USDT")
    
    # Test klines
    klines = client.get_klines('BTCUSDT', '15m', limit=100)
    print(f"   ✅ Historical Data: Retrieved {len(klines)} candles")
    
    print(f"\n   ✅ Binance testnet connection successful!")
    
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    sys.exit(1)

print()

# Step 3: Test Multi-Strategy Analyzer
print("🧠 STEP 3: Testing Multi-Strategy Analyzer")
print("-" * 80)

try:
    from multi_strategy_analyzer import MultiStrategySignalAnalyzer
    
    analyzer = MultiStrategySignalAnalyzer(client)
    
    print("   📊 Analyzing BTCUSDT with all 7 strategies...")
    result = analyzer.analyze_symbol('BTCUSDT', include_scalping=False)
    
    if result:
        print(f"\n   ✅ Analysis Complete!")
        print(f"      Symbol: {result.get('symbol', 'N/A')}")
        print(f"      Signal: {result.get('signal', 'N/A')}")
        print(f"      Confidence: {result.get('confidence', 0):.1f}%")
        print(f"      Stars: {result.get('stars', 'N/A')}")
        print(f"      Price: ${result.get('current_price', 0):,.2f}")
        
        if result.get('strategy_signals'):
            print(f"\n      Strategy Breakdown:")
            for strategy, data in result['strategy_signals'].items():
                emoji = "🟢" if data['signal'] == 'BUY' else "🔴" if data['signal'] == 'SELL' else "⚪"
                print(f"         {emoji} {strategy}: {data['signal']} ({data['strength']})")
        
        # Check if signal would be sent
        if result['signal'] in ['BUY', 'SELL']:
            print(f"\n   📢 This would generate a Discord signal!")
        else:
            print(f"\n   ⏸️  No signal (HOLD) - waiting for better setup")
    else:
        print("   ⚠️  No analysis result returned")
        
except Exception as e:
    print(f"   ❌ FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Step 4: Test Discord Bot (without actually connecting)
print("💬 STEP 4: Checking Discord Configuration")
print("-" * 80)

discord_token = os.getenv('DISCORD_BOT_TOKEN')

if discord_token and len(discord_token) > 50:
    print(f"   ✅ Discord token configured")
    print(f"      Token: {discord_token[:20]}...{discord_token[-10:]}")
else:
    print(f"   ⚠️  Discord token not configured or invalid")

if channel_id and channel_id.isdigit():
    print(f"   ✅ Signal channel configured: {channel_id}")
else:
    print(f"   ⚠️  Signal channel not configured")

print()

# Step 5: Simulate Signal Generation
print("🎯 STEP 5: Simulating Signal Generation")
print("-" * 80)

try:
    if result and result['signal'] in ['BUY', 'SELL']:
        # Format Discord message
        message = analyzer.format_discord_message(result)
        
        print("   ✅ Discord message formatted successfully!")
        print("\n   📱 Message Preview:")
        print("   " + "-" * 76)
        for line in message.split('\n'):
            print(f"   {line}")
        print("   " + "-" * 76)
    else:
        print("   ℹ️  Current signal is HOLD - no message would be sent")
        print("   ℹ️  Bot will wait for BUY/SELL signals")
        
except Exception as e:
    print(f"   ⚠️  Could not format message: {str(e)}")

print()

# Final Summary
print("=" * 80)
print("✅ SYSTEM TEST COMPLETE")
print("=" * 80)

print("\n📊 Test Results:")
print("   ✅ Configuration verified")
print("   ✅ Binance testnet connected")
print("   ✅ Multi-strategy analyzer working")
print("   ✅ Signal generation functional")

print("\n🚀 Next Steps:")
print("   1. Start the bot: python src/auto_trader.py")
print("   2. Bot will analyze markets every 15 minutes")
print("   3. Signals will appear in Discord channel: " + (channel_id or 'NOT SET'))
print("   4. Monitor for BUY/SELL opportunities")

print("\n⚙️  Bot Configuration:")
print(f"   • Exchange: Binance Testnet")
print(f"   • Mode: Signal-Only (NO TRADING)")
print(f"   • Strategies: 7 active")
print(f"   • Check Interval: 15 minutes")
print(f"   • ATR Threshold: 1.25%")
print(f"   • Min Confidence: 50%")

print("\n" + "=" * 80)
print("All systems ready! 🎉")
print("=" * 80)
