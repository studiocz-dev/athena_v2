"""
Comprehensive Bybit Demo API Test
Tests all API functionality with provided keys
"""
import sys
sys.path.insert(0, 'I:\\Discord_Bot\\athena_bot\\src')

from bybit_client import BybitFuturesClient
import os
from dotenv import load_dotenv

load_dotenv()

# Use the keys you provided
API_KEY = "JdYBjx0FgfF8LlgYIv"
API_SECRET = "sX1udIRaiVlYUsYiX8IAM54wzZ0whURiLtk5"

print("="*70)
print("🔑 BYBIT DEMO API COMPREHENSIVE TEST")
print("="*70)
print(f"\nAPI Key: {API_KEY}")
print(f"API Secret: {API_SECRET[:10]}...")
print(f"Mode: DEMO (Testnet)")

try:
    # Initialize client
    print("\n" + "="*70)
    print("1️⃣  TESTING CONNECTION")
    print("="*70)
    
    client = BybitFuturesClient(API_KEY, API_SECRET, demo=True)
    print("✅ Client initialized successfully")
    
    # Test 1: Public Market Data
    print("\n" + "="*70)
    print("2️⃣  TESTING PUBLIC MARKET DATA (No Auth Required)")
    print("="*70)
    
    print("\n📊 BTC Price:")
    btc_price = client.get_current_price('BTCUSDT')
    print(f"   BTCUSDT: ${btc_price:,.2f}")
    
    print("\n📊 ETH Price:")
    eth_price = client.get_current_price('ETHUSDT')
    print(f"   ETHUSDT: ${eth_price:,.2f}")
    
    print("\n📊 Symbol Info:")
    info = client.get_symbol_info('BTCUSDT')
    if info:
        print(f"   Min Qty: {info['min_qty']}")
        print(f"   Max Leverage: {info['max_leverage']}")
        print(f"   Tick Size: {info['tick_size']}")
    
    print("\n📊 15-Min Klines:")
    klines = client.get_klines('BTCUSDT', '15m', limit=5)
    if klines:
        print(f"   Candles received: {len(klines)}")
        print(f"   Latest close: ${klines[-1]['close']:,.2f}")
        print("   ✅ Market data working perfectly!")
    
    # Test 2: Account Balance (Requires Auth)
    print("\n" + "="*70)
    print("3️⃣  TESTING ACCOUNT ACCESS (Requires Auth)")
    print("="*70)
    
    print("\n💰 Account Balance:")
    try:
        balances = client.get_account_balance()
        if balances:
            print("   ✅ AUTHENTICATION SUCCESSFUL!")
            for coin, balance in balances.items():
                print(f"   {coin}: ${balance['wallet_balance']:,.2f}")
        else:
            print("   ⚠️  No balance data (might be empty account)")
            print("   ℹ️  Get demo funds from: https://testnet.bybit.com/app/user/wallet")
    except Exception as e:
        print(f"   ❌ Auth failed: {e}")
        print("\n   📝 This means:")
        print("   - Keys might be for LIVE trading (not testnet)")
        print("   - OR keys need to be regenerated")
        print("   - OR need testnet keys from: https://testnet.bybit.com/")
    
    # Test 3: Position Info
    print("\n📊 Open Positions:")
    try:
        positions = client.get_position_info()
        if positions:
            print(f"   Open positions: {len(positions)}")
            for pos in positions:
                print(f"   {pos['symbol']}: {pos['side']} {pos['position_amount']}")
        else:
            print("   No open positions")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Leverage Setting (Requires Auth)
    print("\n" + "="*70)
    print("4️⃣  TESTING LEVERAGE SETTING")
    print("="*70)
    
    try:
        result = client.set_leverage('BTCUSDT', 10)
        if result:
            print("   ✅ Leverage set successfully to 10x")
        else:
            print("   ❌ Failed to set leverage")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Order Placement (Requires Auth - but we won't actually place)
    print("\n" + "="*70)
    print("5️⃣  ORDER PLACEMENT TEST (Simulation)")
    print("="*70)
    
    print("\n📝 Simulating market order:")
    print(f"   Symbol: BTCUSDT")
    print(f"   Side: Buy")
    print(f"   Quantity: 0.001 BTC")
    print(f"   Type: Market")
    print("\n   ⏭️  Skipping actual order (test mode)")
    print("   ℹ️  To test real orders, manually place test trade on testnet")
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    print("\n✅ WORKING:")
    print("   • Client initialization")
    print("   • Public market data (prices, klines, symbol info)")
    print("   • Price fetching")
    
    print("\n⏳ NEEDS VERIFICATION:")
    print("   • Account balance access")
    print("   • Position management")
    print("   • Order placement")
    print("   • Leverage settings")
    
    print("\n💡 RECOMMENDATION:")
    print("   If auth tests failed:")
    print("   1. Get testnet keys from: https://testnet.bybit.com/app/user/api-management")
    print("   2. Enable these permissions:")
    print("      - Unified Trading - Trade (Read-Write)")
    print("      - Contracts - Orders, Positions (Read-Write)")
    print("   3. Update .env with new testnet keys")
    print("\n   If auth tests passed:")
    print("   1. Get demo USDT from testnet faucet")
    print("   2. Ready to deploy!")
    
    print("\n" + "="*70)
    print("✅ BYBIT CLIENT TEST COMPLETE")
    print("="*70)

except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
