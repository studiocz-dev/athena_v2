"""Test Bybit Demo API Keys"""
from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

api_key = "JdYBjx0FgfF8LlgYIv"
api_secret = "sX1udIRaiVlYUsYiX8IAM54wzZ0whURiLtk5"

print("🔑 Testing Bybit Demo API Keys...")
print(f"API Key: {api_key}")
print(f"API Secret: {api_secret[:10]}...")

# Test connection
client = HTTP(
    testnet=True,
    api_key=api_key,
    api_secret=api_secret
)

print("\n1. Testing server time (public)...")
try:
    response = client.get_server_time()
    print(f"✅ Server time: {response}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n2. Testing market data (public)...")
try:
    response = client.get_tickers(
        category="linear",
        symbol="BTCUSDT"
    )
    print(f"✅ BTC Price: ${response['result']['list'][0]['lastPrice']}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n3. Testing wallet balance (requires auth)...")
try:
    response = client.get_wallet_balance(
        accountType="UNIFIED"
    )
    print(f"✅ Wallet: {response}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n4. Testing with CONTRACT account type...")
try:
    response = client.get_wallet_balance(
        accountType="CONTRACT"
    )
    print(f"✅ Contract Wallet: {response}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n5. Testing API key info...")
try:
    response = client.get_api_key_information()
    print(f"✅ API Key Info: {response}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n6. Testing positions (requires auth)...")
try:
    response = client.get_positions(
        category="linear",
        settleCoin="USDT"
    )
    print(f"✅ Positions: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
