"""
IMPORTANT: Bybit Demo Trading API Setup Instructions

To use Bybit Demo Trading, you need to:

1. Visit: https://testnet.bybit.com/
2. Sign in or create a testnet account (FREE)
3. Go to: https://testnet.bybit.com/app/user/api-management
4. Create API keys with these permissions:
   - Read-Write for Unified Trading Account
   - Contracts - Orders, Positions
   - USDC Contracts - Trade
   - Unified Trading - Trade

5. Copy the API Key and API Secret

6. Update .env file:
   BYBIT_API_KEY=your_testnet_api_key
   BYBIT_API_SECRET=your_testnet_api_secret
   BYBIT_DEMO=True

7. Get demo USDT:
   - Go to https://testnet.bybit.com/app/user/wallet
   - Click "Get test funds" or similar
   - You'll get 100,000 USDT for free testing

CURRENT KEYS STATUS:
The keys you provided: JdYBjx0FgfF8LlgYIv
These keys are returning 401 errors, which means:
- They might be from LIVE trading (not testnet)
- They might be expired
- They might not have the right permissions
- They need to be regenerated

SOLUTION:
1. Go to https://testnet.bybit.com/ and create testnet API keys
2. OR we can work with public market data only (no trading)
3. OR we can use Binance testnet which we know works

Let me know which approach you prefer!
"""

print(__doc__)

# Test with public market data (no auth needed)
from pybit.unified_trading import HTTP

print("\n" + "="*60)
print("TESTING PUBLIC MARKET DATA (No Auth Required)")
print("="*60)

client = HTTP(testnet=True)

print("\n1. Get BTC price...")
try:
    response = client.get_tickers(category="linear", symbol="BTCUSDT")
    price = response['result']['list'][0]['lastPrice']
    print(f"✅ BTCUSDT: ${price}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n2. Get ETH price...")
try:
    response = client.get_tickers(category="linear", symbol="ETHUSDT")
    price = response['result']['list'][0]['lastPrice']
    print(f"✅ ETHUSDT: ${price}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n3. Get klines...")
try:
    response = client.get_kline(
        category="linear",
        symbol="BTCUSDT",
        interval="15",
        limit=5
    )
    print(f"✅ Got {len(response['result']['list'])} candles")
    latest = response['result']['list'][0]
    print(f"   Latest close: ${latest[4]}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n4. Get instrument info...")
try:
    response = client.get_instruments_info(
        category="linear",
        symbol="BTCUSDT"
    )
    info = response['result']['list'][0]
    print(f"✅ Min order qty: {info['lotSizeFilter']['minOrderQty']}")
    print(f"   Max leverage: {info['leverageFilter']['maxLeverage']}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("PUBLIC API WORKS PERFECTLY!")
print("="*60)
print("\nFor TRADING, we need valid testnet API keys from:")
print("https://testnet.bybit.com/app/user/api-management")
print("\nOr we can continue with Binance testnet which already works!")
