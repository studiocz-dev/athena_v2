"""
Test both Gate.io testnet and live endpoints to determine which keys work
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gate_client import GateClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_endpoint(testnet: bool):
    """Test a specific endpoint"""
    endpoint_name = "TESTNET" if testnet else "LIVE"
    print(f"\n{'='*60}")
    print(f"Testing {endpoint_name} Endpoint")
    print(f"{'='*60}")
    
    api_key = os.getenv('GATE_API_KEY')
    api_secret = os.getenv('GATE_API_SECRET')
    
    try:
        client = GateClient(api_key, api_secret, testnet=testnet)
        
        # Test public endpoint
        print("\n1️⃣ Testing public endpoint...")
        price = client.get_current_price('BTCUSDT')
        print(f"   ✅ BTC Price: ${price:,.2f}")
        
        # Test private endpoint
        print("\n2️⃣ Testing private endpoint...")
        balance = client.get_account_balance()
        print(f"   ✅ Account Balance: {balance['total']} USDT")
        print(f"   ✅ Available: {balance['available']} USDT")
        
        return True, f"{endpoint_name} keys work!"
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "INVALID_SIGNATURE" in error_msg:
            print(f"   ❌ Authentication failed - keys don't work on {endpoint_name}")
        else:
            print(f"   ❌ Error: {error_msg}")
        return False, error_msg

def main():
    """Test both endpoints"""
    
    api_key = os.getenv('GATE_API_KEY')
    api_secret = os.getenv('GATE_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ Error: GATE_API_KEY and GATE_API_SECRET not found in .env")
        return
    
    print("=" * 60)
    print("Gate.io API Keys Test")
    print("=" * 60)
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test testnet
    testnet_success, testnet_msg = test_endpoint(testnet=True)
    
    # Test live
    live_success, live_msg = test_endpoint(testnet=False)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if testnet_success:
        print("✅ TESTNET KEYS - Ready to use!")
        print("\nAction: Already configured correctly in .env")
        print("   EXCHANGE=gate")
        print("   GATE_TESTNET=True")
    elif live_success:
        print("✅ LIVE KEYS - Keys work on live endpoint")
        print("\n⚠️  WARNING: These are LIVE trading keys, not testnet!")
        print("\nOptions:")
        print("   A) Use live endpoint (small positions recommended)")
        print("   B) Generate proper testnet keys at testnet.gate.io")
        print("\nTo use live endpoint, update .env:")
        print("   GATE_TESTNET=False")
    else:
        print("❌ KEYS DON'T WORK on either endpoint")
        print("\nPossible issues:")
        print("   1. Keys are incorrect")
        print("   2. Keys don't have futures trading permission")
        print("   3. Keys are for spot trading only")
        print("\nSolution:")
        print("   - Verify keys at gate.io → API Management")
        print("   - Ensure 'Futures' permission is enabled")
        print("   - For testnet: generate keys at testnet.gate.io")

if __name__ == "__main__":
    main()
