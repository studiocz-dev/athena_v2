"""
Quick test to verify Bybit demo keys work
"""
from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('BYBIT_API_KEY')
api_secret = os.getenv('BYBIT_API_SECRET')

print(f"Testing Bybit DEMO keys...")
print(f"API Key: {api_key}")
print(f"Using testnet=True")

try:
    # Initialize client
    client = HTTP(
        testnet=True,
        api_key=api_key,
        api_secret=api_secret
    )
    
    print("\n1. Testing connection...")
    server_time = client.get_server_time()
    print(f"✅ Server time: {server_time['result']['timeSecond']}")
    
    print("\n2. Testing market data (no auth)...")
    ticker = client.get_tickers(category="linear", symbol="BTCUSDT")
    price = float(ticker['result']['list'][0]['lastPrice'])
    print(f"✅ BTC Price: ${price:,.2f}")
    
    print("\n3. Testing account balance (requires auth)...")
    balance = client.get_wallet_balance(accountType="UNIFIED", coin="USDT")
    print(f"✅ Response: {balance}")
    
    if balance['retCode'] == 0:
        print("✅ AUTHENTICATION SUCCESSFUL!")
        total = balance['result']['list'][0]['totalEquity']
        print(f"✅ Total Balance: {total} USDT")
    else:
        print(f"❌ Auth failed: {balance['retMsg']}")
        
    print("\n4. Testing positions...")
    positions = client.get_positions(category="linear", settleCoin="USDT")
    print(f"Response: {positions}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
