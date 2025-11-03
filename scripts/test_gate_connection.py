"""
Test Gate.io API Connection
Verify testnet keys work properly
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gate_client import GateClient, test_gate_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Test Gate.io API connection"""
    
    api_key = os.getenv('GATE_API_KEY')
    api_secret = os.getenv('GATE_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ Error: GATE_API_KEY and GATE_API_SECRET not found in .env")
        print("\nPlease add to .env:")
        print("GATE_API_KEY=your_key_here")
        print("GATE_API_SECRET=your_secret_here")
        return
    
    print("🔑 Using API Key:", api_key[:10] + "..." + api_key[-4:])
    print()
    
    # Run comprehensive test
    test_gate_client(api_key, api_secret)
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("✅ If all tests passed:")
    print("   1. Gate.io testnet is ready!")
    print("   2. Run: python src/auto_trader.py")
    print("   3. Watch signals in Discord channel")
    print("\n❌ If tests failed:")
    print("   1. Verify keys are correct")
    print("   2. Check testnet.gate.io has futures enabled")
    print("   3. Ensure API permissions include futures trading")


if __name__ == "__main__":
    main()
