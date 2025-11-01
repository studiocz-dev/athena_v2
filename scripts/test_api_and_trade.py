"""
Test Binance TESTNET API Connection and Execute Test Trade
"""

import sys
import os
# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

from binance_client import BinanceFuturesClient
import config
import time

BINANCE_API_KEY = config.BINANCE_API_KEY
BINANCE_API_SECRET = config.BINANCE_API_SECRET

def test_api_connection():
    """Test API connection and permissions"""
    print("=" * 70)
    print("🔧 TESTING BINANCE TESTNET API CONNECTION")
    print("=" * 70)
    
    # Initialize client with TESTNET=True
    client = BinanceFuturesClient(
        BINANCE_API_KEY,
        BINANCE_API_SECRET,
        testnet=True  # Force testnet
    )
    
    print(f"\n✅ Client initialized")
    print(f"📍 Environment: {'TESTNET' if client.testnet else 'MAINNET'}")
    
    # Test 1: Get account balance
    print("\n" + "-" * 70)
    print("TEST 1: Getting Account Information")
    print("-" * 70)
    try:
        balances = client.get_account_balance()
        if balances and len(balances) > 0:  # Check if not empty dict
            print("✅ Account info retrieved successfully!")
            print(f"📊 Total Assets: {len(balances)}")
            
            # Show USDT balance
            if 'USDT' in balances:
                wallet_balance = balances['USDT']['wallet_balance']
                available_balance = balances['USDT']['available_balance']
                unrealized_pnl = balances['USDT']['unrealized_pnl']
                print(f"💰 USDT Wallet Balance: {wallet_balance:.2f}")
                print(f"💵 USDT Available: {available_balance:.2f}")
                print(f"📊 Unrealized P&L: {unrealized_pnl:.2f}")
            else:
                print("⚠️  No USDT balance found (might be zero)")
        else:
            print("❌ Failed to get account info - API key error")
            print("\n" + "=" * 70)
            print("⚠️⚠️⚠️  API KEY ERROR - TESTNET KEYS REQUIRED  ⚠️⚠️⚠️")
            print("=" * 70)
            print("\nYour current API keys are for MAINNET, not TESTNET!")
            print("\nTo get TESTNET API keys:")
            print("1. Go to: https://testnet.binancefuture.com/")
            print("2. Login/register (testnet account is separate from mainnet)")
            print("3. Go to API Management")
            print("4. Create new API key")
            print("5. Update .env file with TESTNET keys")
            print("\nAlternatively:")
            print("- Set BINANCE_TESTNET=False in .env to test on MAINNET")
            print("- ⚠️  WARNING: MAINNET uses REAL MONEY!")
            print("=" * 70)
            return False
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error getting account info: {error_msg}")
        
        if "Invalid API-key" in error_msg or "-2015" in error_msg:
            print("\n" + "=" * 70)
            print("⚠️⚠️⚠️  API KEY ERROR - TESTNET KEYS REQUIRED  ⚠️⚠️⚠️")
            print("=" * 70)
            print("\nYour current API keys are for MAINNET, not TESTNET!")
            print("\nTo get TESTNET API keys:")
            print("1. Go to: https://testnet.binancefuture.com/")
            print("2. Login/register (testnet account is separate from mainnet)")
            print("3. Go to API Management")
            print("4. Create new API key")
            print("5. Update .env file with TESTNET keys")
            print("\nAlternatively:")
            print("- Set BINANCE_TESTNET=False in .env to test on MAINNET")
            print("- ⚠️  WARNING: MAINNET uses REAL MONEY!")
            print("=" * 70)
        
        return False
    
    # Test 2: Get current price
    print("\n" + "-" * 70)
    print("TEST 2: Getting Market Data")
    print("-" * 70)
    try:
        symbol = 'BTCUSDT'
        price = client.get_current_price(symbol)
        if price:
            print(f"✅ Market data retrieved successfully!")
            print(f"📈 {symbol} Price: ${price:,.2f}")
        else:
            print("❌ Failed to get market data")
            return False
    except Exception as e:
        print(f"❌ Error getting market data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Get open positions
    print("\n" + "-" * 70)
    print("TEST 3: Getting Open Positions")
    print("-" * 70)
    try:
        positions = client.get_position_info()
        if positions is not None:
            open_positions = [p for p in positions if float(p.get('positionAmt', 0)) != 0]
            print(f"✅ Positions retrieved successfully!")
            print(f"📊 Total Positions: {len(positions)}")
            print(f"📈 Open Positions: {len(open_positions)}")
            
            if open_positions:
                print("\n🔍 Open Positions:")
                for pos in open_positions:
                    symbol = pos['symbol']
                    amount = float(pos['positionAmt'])
                    entry_price = float(pos['entryPrice'])
                    pnl = float(pos['unRealizedProfit'])
                    print(f"   {symbol}: {amount} @ ${entry_price:.4f} | P&L: ${pnl:.2f}")
        else:
            print("❌ Failed to get positions")
            return False
    except Exception as e:
        print(f"❌ Error getting positions: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL API TESTS PASSED!")
    print("=" * 70)
    return True

def execute_test_trade():
    """Execute a small test trade on TESTNET"""
    print("\n" + "=" * 70)
    print("🎯 EXECUTING TEST TRADE")
    print("=" * 70)
    
    client = BinanceFuturesClient(
        BINANCE_API_KEY,
        BINANCE_API_SECRET,
        testnet=True
    )
    
    symbol = 'BTCUSDT'
    
    # Get current price
    print(f"\n📊 Getting current {symbol} price...")
    current_price = client.get_current_price(symbol)
    print(f"💵 Current Price: ${current_price:,.2f}")
    
    # Calculate trade parameters
    position_size_usdt = 100  # Increase to $100 for minimum quantity
    quantity = position_size_usdt / current_price
    
    # BTC futures requires minimum 0.001 BTC
    if quantity < 0.001:
        quantity = 0.001
        position_size_usdt = quantity * current_price
        print(f"⚠️  Adjusted to minimum quantity: 0.001 BTC (${position_size_usdt:.2f})")
    
    quantity = round(quantity, 3)  # Round to 3 decimals for BTC
    
    print(f"\n📝 Trade Parameters:")
    print(f"   Symbol: {symbol}")
    print(f"   Side: BUY (LONG)")
    print(f"   Position Size: ${position_size_usdt}")
    print(f"   Quantity: {quantity} BTC")
    print(f"   Entry Price: ${current_price:,.2f}")
    
    # Calculate stop-loss and take-profit (round to 2 decimals for price precision)
    stop_loss = round(current_price * 0.98, 2)  # 2% below entry
    take_profit = round(current_price * 1.04, 2)  # 4% above entry (2:1 R:R)
    
    print(f"   Stop Loss: ${stop_loss:,.2f} (-2%)")
    print(f"   Take Profit: ${take_profit:,.2f} (+4%)")
    print(f"   Risk/Reward: 1:2")
    
    # Ask for confirmation
    print("\n⚠️  This will place a REAL order on TESTNET")
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Trade cancelled by user")
        return None
    
    # Place market order
    print("\n🚀 Placing MARKET BUY order...")
    try:
        order = client.place_market_order(
            symbol=symbol,
            side='BUY',
            quantity=quantity
        )
        
        if order and 'orderId' in order:
            order_id = order['orderId']
            filled_price = float(order.get('avgPrice', current_price))
            filled_qty = float(order.get('executedQty', quantity))
            
            print(f"✅ Order executed successfully!")
            print(f"📋 Order ID: {order_id}")
            print(f"💰 Filled Price: ${filled_price:,.2f}")
            print(f"📊 Filled Quantity: {filled_qty} BTC")
            print(f"💵 Total Value: ${filled_price * filled_qty:,.2f}")
            
            # Place stop-loss order
            print(f"\n🛡️  Placing STOP-LOSS order at ${stop_loss:,.2f}...")
            try:
                sl_order = client.place_stop_loss(
                    symbol=symbol,
                    side='SELL',
                    quantity=filled_qty,
                    stop_price=stop_loss
                )
                
                if sl_order and 'orderId' in sl_order:
                    print(f"✅ Stop-loss placed: Order ID {sl_order['orderId']}")
                else:
                    print("⚠️  Failed to place stop-loss order")
            except Exception as e:
                print(f"⚠️  Error placing stop-loss: {e}")
            
            # Place take-profit order
            print(f"\n🎯 Placing TAKE-PROFIT order at ${take_profit:,.2f}...")
            try:
                tp_order = client.place_take_profit(
                    symbol=symbol,
                    side='SELL',
                    quantity=filled_qty,
                    stop_price=take_profit
                )
                
                if tp_order and 'orderId' in tp_order:
                    print(f"✅ Take-profit placed: Order ID {tp_order['orderId']}")
                else:
                    print("⚠️  Failed to place take-profit order")
            except Exception as e:
                print(f"⚠️  Error placing take-profit: {e}")
            
            print("\n" + "=" * 70)
            print("✅ TEST TRADE COMPLETE!")
            print("=" * 70)
            print(f"\n📊 Position Summary:")
            print(f"   Symbol: {symbol}")
            print(f"   Side: LONG")
            print(f"   Entry: ${filled_price:,.2f}")
            print(f"   Quantity: {filled_qty} BTC")
            print(f"   Stop Loss: ${stop_loss:,.2f}")
            print(f"   Take Profit: ${take_profit:,.2f}")
            
            return order
        else:
            print(f"❌ Order failed: {order}")
            return None
            
    except Exception as e:
        print(f"❌ Error placing order: {e}")
        import traceback
        traceback.print_exc()
        return None

def close_test_position():
    """Close the test position"""
    print("\n" + "=" * 70)
    print("🔴 CLOSING TEST POSITION")
    print("=" * 70)
    
    client = BinanceFuturesClient(
        BINANCE_API_KEY,
        BINANCE_API_SECRET,
        testnet=True
    )
    
    symbol = 'BTCUSDT'
    
    # Get current position
    print(f"\n🔍 Checking current position in {symbol}...")
    positions = client.get_position_info(symbol)
    btc_position = None
    
    for pos in positions:
        if pos['symbol'] == symbol:
            btc_position = pos
            break
    
    if not btc_position:
        print(f"❌ No open position found in {symbol}")
        print("   Position may have been auto-closed or never opened")
        return False
    
    position_amt = btc_position['position_amount']
    entry_price = btc_position['entry_price']
    unrealized_pnl = btc_position['unrealized_pnl']
    
    print(f"✅ Position found!")
    print(f"   Amount: {position_amt} BTC")
    print(f"   Entry Price: ${entry_price:,.2f}")
    print(f"   Unrealized P&L: ${unrealized_pnl:.2f}")
    
    # Get current price
    current_price = client.get_current_price(symbol)
    print(f"   Current Price: ${current_price:,.2f}")
    
    # Calculate P&L
    pnl_percent = ((current_price - entry_price) / entry_price) * 100
    print(f"   P&L %: {pnl_percent:+.2f}%")
    
    # Ask for confirmation
    print("\n⚠️  This will CLOSE the position at market price")
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Close cancelled by user")
        return False
    
    # Close position (sell the quantity)
    print(f"\n🔴 Closing position with MARKET SELL order...")
    try:
        # Cancel any open orders first
        print("🗑️  Cancelling any open orders...")
        try:
            client.cancel_all_orders(symbol)
            print("✅ Open orders cancelled")
        except:
            pass
        
        # Place market sell order to close (don't use reduce_only for closing)
        close_order = client.place_market_order(
            symbol=symbol,
            side='SELL',
            quantity=abs(position_amt),
            reduce_only=False  # Changed to False to allow closing
        )
        
        if close_order and 'orderId' in close_order:
            exit_price = float(close_order.get('avgPrice', current_price))
            
            print(f"✅ Position closed successfully!")
            print(f"📋 Order ID: {close_order['orderId']}")
            print(f"💰 Exit Price: ${exit_price:,.2f}")
            
            # Calculate final P&L
            final_pnl = (exit_price - entry_price) * abs(position_amt)
            final_pnl_percent = ((exit_price - entry_price) / entry_price) * 100
            
            print("\n" + "=" * 70)
            print("📊 FINAL TRADE RESULTS")
            print("=" * 70)
            print(f"   Entry: ${entry_price:,.2f}")
            print(f"   Exit: ${exit_price:,.2f}")
            print(f"   P&L: ${final_pnl:.2f} ({final_pnl_percent:+.2f}%)")
            print(f"   Quantity: {abs(position_amt)} BTC")
            print(f"   {'✅ PROFIT' if final_pnl > 0 else '❌ LOSS'}")
            
            return True
        else:
            print(f"❌ Failed to close position: {close_order}")
            return False
            
    except Exception as e:
        print(f"❌ Error closing position: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test flow"""
    print("\n🚀 BINANCE TESTNET API TESTING SUITE")
    print("=" * 70)
    
    # Step 1: Test API connection
    if not test_api_connection():
        print("\n❌ API connection tests failed. Please check your API keys.")
        return
    
    # Step 2: Ask if user wants to execute test trade
    print("\n" + "=" * 70)
    execute = input("\n🎯 Execute test trade? (yes/no): ").strip().lower()
    
    if execute == 'yes':
        order = execute_test_trade()
        
        if order:
            # Wait a moment
            print("\n⏳ Waiting 5 seconds before checking position...")
            time.sleep(5)
            
            # Step 3: Ask if user wants to close position
            close = input("\n🔴 Close test position? (yes/no): ").strip().lower()
            
            if close == 'yes':
                close_test_position()
            else:
                print("\n⚠️  Position left open. You can close it manually later.")
                print("   Run this script again and skip to closing position.")
    
    print("\n" + "=" * 70)
    print("🎉 TESTING COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    main()
