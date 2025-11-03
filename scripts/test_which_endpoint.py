"""
Test Bybit keys on BOTH testnet and live endpoints
This will tell us which environment the keys are for
"""
from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('BYBIT_API_KEY')
api_secret = os.getenv('BYBIT_API_SECRET')

print("=" * 60)
print("TESTING BYBIT API KEYS")
print("=" * 60)
print(f"API Key: {api_key[:10]}...")
print()

# Test 1: TESTNET
print("🧪 TEST 1: TESTNET (api-testnet.bybit.com)")
print("-" * 60)
try:
    client_testnet = HTTP(
        testnet=True,
        api_key=api_key,
        api_secret=api_secret
    )
    
    print("✅ Market data works (no auth):")
    ticker = client_testnet.get_tickers(category="linear", symbol="BTCUSDT")
    print(f"   BTC Price: ${float(ticker['result']['list'][0]['lastPrice']):,.2f}")
    
    print("\n🔐 Testing authentication...")
    balance = client_testnet.get_wallet_balance(accountType="UNIFIED")
    
    if balance['retCode'] == 0:
        print("   ✅ TESTNET AUTH SUCCESSFUL!")
        print(f"   Balance: {balance['result']}")
    else:
        print(f"   ❌ TESTNET AUTH FAILED: {balance['retMsg']}")
        
except Exception as e:
    print(f"   ❌ TESTNET ERROR: {str(e)[:100]}")

print("\n" + "=" * 60)

# Test 2: LIVE
print("🔴 TEST 2: LIVE (api.bybit.com)")
print("-" * 60)
print("⚠️  WARNING: Testing with LIVE endpoint (read-only)")
try:
    client_live = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret
    )
    
    print("✅ Market data works (no auth):")
    ticker = client_live.get_tickers(category="linear", symbol="BTCUSDT")
    print(f"   BTC Price: ${float(ticker['result']['list'][0]['lastPrice']):,.2f}")
    
    print("\n🔐 Testing authentication...")
    balance = client_live.get_wallet_balance(accountType="UNIFIED")
    
    if balance['retCode'] == 0:
        print("   ✅ LIVE AUTH SUCCESSFUL!")
        print("   ⚠️  YOUR KEYS ARE FOR LIVE TRADING!")
        total = balance['result']['list'][0]['totalEquity']
        print(f"   Balance: {total} USDT (REAL MONEY)")
    else:
        print(f"   ❌ LIVE AUTH FAILED: {balance['retMsg']}")
        
except Exception as e:
    print(f"   ❌ LIVE ERROR: {str(e)[:100]}")

print("\n" + "=" * 60)
print("CONCLUSION:")
print("=" * 60)
print("✅ If TESTNET auth worked → Keys are for demo trading")
print("⚠️  If LIVE auth worked → Keys are for real trading")
print("❌ If both failed → Keys may be invalid or have wrong permissions")
print("=" * 60)
