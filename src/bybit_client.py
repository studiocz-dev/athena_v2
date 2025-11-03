"""
Bybit Futures Trading Client
Handles API interactions with Bybit Derivatives (Demo Trading)
"""
from pybit.unified_trading import HTTP
from typing import Dict, List, Optional, Tuple
import time
from logger import get_logger
import config

log = get_logger('BybitClient')


class BybitFuturesClient:
    """Wrapper for Bybit Unified Trading API with safety features"""
    
    def __init__(self, api_key: str, api_secret: str, demo: bool = True):
        """
        Initialize Bybit Unified Trading client
        
        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
            demo: Use demo trading if True (default)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.demo = demo
        
        # Initialize client
        if demo:
            self.client = HTTP(
                testnet=True,
                api_key=api_key,
                api_secret=api_secret
            )
            log.info("✅ Connected to Bybit DEMO Trading (Testnet)")
        else:
            self.client = HTTP(
                testnet=False,
                api_key=api_key,
                api_secret=api_secret
            )
            log.info("⚠️ Connected to Bybit LIVE Trading")
        
        # Test connection
        try:
            self.test_connection()
        except Exception as e:
            log.error(f"❌ Failed to connect to Bybit: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.client.get_server_time()
            if response['retCode'] == 0:
                log.info(f"✅ Bybit server time: {response['result']['timeSecond']}")
                return True
            else:
                log.error(f"❌ Connection test failed: {response}")
                return False
        except Exception as e:
            log.error(f"❌ Connection error: {e}")
            return False
    
    def get_account_balance(self) -> Dict:
        """Get futures account balance"""
        try:
            # Get wallet balance for USDT perpetual
            response = self.client.get_wallet_balance(
                accountType="UNIFIED"  # Unified trading account
            )
            
            if response['retCode'] != 0:
                log.error(f"Error getting balance: {response['retMsg']}")
                return {}
            
            balances = {}
            for coin in response['result']['list'][0]['coin']:
                if float(coin['walletBalance']) > 0:
                    balances[coin['coin']] = {
                        'wallet_balance': float(coin['walletBalance']),
                        'available_balance': float(coin['availableToWithdraw']),
                        'unrealized_pnl': float(coin.get('unrealisedPnl', 0))
                    }
            
            return balances
        except Exception as e:
            log.error(f"Error getting account balance: {e}")
            return {}
    
    def get_position_info(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open positions
        
        Args:
            symbol: Specific symbol to query (e.g., 'BTCUSDT'), or None for all
            
        Returns:
            List of position dictionaries
        """
        try:
            params = {
                "category": "linear",  # USDT perpetual
                "settleCoin": "USDT"
            }
            if symbol:
                params['symbol'] = symbol
            
            response = self.client.get_positions(**params)
            
            if response['retCode'] != 0:
                log.error(f"Error getting positions: {response['retMsg']}")
                return []
            
            open_positions = []
            for pos in response['result']['list']:
                position_size = float(pos['size'])
                if position_size > 0:
                    open_positions.append({
                        'symbol': pos['symbol'],
                        'position_amount': position_size if pos['side'] == 'Buy' else -position_size,
                        'entry_price': float(pos['avgPrice']),
                        'mark_price': float(pos['markPrice']),
                        'unrealized_pnl': float(pos['unrealisedPnl']),
                        'leverage': int(float(pos['leverage'])),
                        'liquidation_price': float(pos.get('liqPrice', 0)) if pos.get('liqPrice') else 0,
                        'side': 'LONG' if pos['side'] == 'Buy' else 'SHORT'
                    })
            
            return open_positions
        except Exception as e:
            log.error(f"Error getting position info: {e}")
            return []
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Get trading rules and symbol information"""
        try:
            response = self.client.get_instruments_info(
                category="linear",
                symbol=symbol
            )
            
            if response['retCode'] != 0:
                log.error(f"Error getting symbol info: {response['retMsg']}")
                return {}
            
            info = response['result']['list'][0]
            return {
                'symbol': info['symbol'],
                'min_qty': float(info['lotSizeFilter']['minOrderQty']),
                'max_qty': float(info['lotSizeFilter']['maxOrderQty']),
                'qty_step': float(info['lotSizeFilter']['qtyStep']),
                'min_price': float(info['priceFilter']['minPrice']),
                'max_price': float(info['priceFilter']['maxPrice']),
                'tick_size': float(info['priceFilter']['tickSize']),
                'min_notional': 0,  # Bybit doesn't have min notional
                'max_leverage': int(float(info['leverageFilter']['maxLeverage']))
            }
        except Exception as e:
            log.error(f"Error getting symbol info: {e}")
            return {}
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """
        Get historical klines/candlesticks
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe ('1', '5', '15', '60', '240', 'D')
            limit: Number of candles to fetch
            
        Returns:
            List of kline dictionaries
        """
        try:
            # Convert interval format (Binance style to Bybit style)
            interval_map = {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '1h': '60',
                '4h': '240',
                '1d': 'D'
            }
            bybit_interval = interval_map.get(interval, interval)
            
            response = self.client.get_kline(
                category="linear",
                symbol=symbol,
                interval=bybit_interval,
                limit=limit
            )
            
            if response['retCode'] != 0:
                log.error(f"Error getting klines: {response['retMsg']}")
                return []
            
            klines = []
            for k in response['result']['list']:
                klines.append({
                    'timestamp': int(k[0]),
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5])
                })
            
            # Bybit returns newest first, reverse to match Binance (oldest first)
            klines.reverse()
            return klines
            
        except Exception as e:
            log.error(f"Error getting klines for {symbol}: {e}")
            return []
    
    def get_current_price(self, symbol: str) -> float:
        """Get current market price"""
        try:
            response = self.client.get_tickers(
                category="linear",
                symbol=symbol
            )
            
            if response['retCode'] != 0:
                log.error(f"Error getting price: {response['retMsg']}")
                return 0.0
            
            return float(response['result']['list'][0]['lastPrice'])
        except Exception as e:
            log.error(f"Error getting current price: {e}")
            return 0.0
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage for symbol"""
        try:
            response = self.client.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            
            if response['retCode'] == 0:
                log.info(f"✅ Set {symbol} leverage to {leverage}x")
                return True
            else:
                log.error(f"Error setting leverage: {response['retMsg']}")
                return False
        except Exception as e:
            log.error(f"Error setting leverage: {e}")
            return False
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float,
                   price: Optional[float] = None, stop_loss: Optional[float] = None,
                   take_profit: Optional[float] = None) -> Optional[Dict]:
        """
        Place an order
        
        Args:
            symbol: Trading pair
            side: 'Buy' or 'Sell'
            order_type: 'Market' or 'Limit'
            quantity: Order quantity
            price: Limit price (required for limit orders)
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Order details or None if failed
        """
        try:
            params = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": str(quantity),
                "timeInForce": "GTC"  # Good Till Cancel
            }
            
            if order_type == "Limit" and price:
                params['price'] = str(price)
            
            if stop_loss:
                params['stopLoss'] = str(stop_loss)
            
            if take_profit:
                params['takeProfit'] = str(take_profit)
            
            response = self.client.place_order(**params)
            
            if response['retCode'] == 0:
                order = response['result']
                log.info(f"✅ Order placed: {side} {quantity} {symbol} @ {price if price else 'Market'}")
                return {
                    'order_id': order['orderId'],
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'status': 'NEW'
                }
            else:
                log.error(f"❌ Order failed: {response['retMsg']}")
                return None
                
        except Exception as e:
            log.error(f"Error placing order: {e}")
            return None
    
    def place_market_order(self, symbol: str, side: str, quantity: float,
                          stop_loss: Optional[float] = None,
                          take_profit: Optional[float] = None) -> Optional[Dict]:
        """Place a market order"""
        return self.place_order(symbol, side, "Market", quantity, 
                              stop_loss=stop_loss, take_profit=take_profit)
    
    def close_position(self, symbol: str, side: str = None) -> bool:
        """
        Close an open position
        
        Args:
            symbol: Symbol to close
            side: 'LONG' or 'SHORT' (if None, will determine from position)
            
        Returns:
            True if successful
        """
        try:
            # Get current position to determine side and quantity
            positions = self.get_position_info(symbol)
            if not positions:
                log.warning(f"No open position for {symbol}")
                return False
            
            position = positions[0]
            pos_side = position['side']
            pos_qty = abs(position['position_amount'])
            
            # Determine closing side
            close_side = 'Sell' if pos_side == 'LONG' else 'Buy'
            
            # Place market order to close
            response = self.client.place_order(
                category="linear",
                symbol=symbol,
                side=close_side,
                orderType="Market",
                qty=str(pos_qty),
                reduceOnly=True  # Important: only reduce position
            )
            
            if response['retCode'] == 0:
                log.info(f"✅ Closed {pos_side} position: {symbol}")
                return True
            else:
                log.error(f"❌ Failed to close position: {response['retMsg']}")
                return False
                
        except Exception as e:
            log.error(f"Error closing position: {e}")
            return False
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an open order"""
        try:
            response = self.client.cancel_order(
                category="linear",
                symbol=symbol,
                orderId=order_id
            )
            
            if response['retCode'] == 0:
                log.info(f"✅ Cancelled order {order_id}")
                return True
            else:
                log.error(f"Error cancelling order: {response['retMsg']}")
                return False
        except Exception as e:
            log.error(f"Error cancelling order: {e}")
            return False
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open orders"""
        try:
            params = {
                "category": "linear",
                "settleCoin": "USDT"
            }
            if symbol:
                params['symbol'] = symbol
            
            response = self.client.get_open_orders(**params)
            
            if response['retCode'] != 0:
                log.error(f"Error getting open orders: {response['retMsg']}")
                return []
            
            orders = []
            for order in response['result']['list']:
                orders.append({
                    'order_id': order['orderId'],
                    'symbol': order['symbol'],
                    'side': order['side'],
                    'type': order['orderType'],
                    'quantity': float(order['qty']),
                    'price': float(order['price']) if order.get('price') else 0,
                    'status': order['orderStatus']
                })
            
            return orders
        except Exception as e:
            log.error(f"Error getting open orders: {e}")
            return []
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                               risk_amount: float, stop_loss_percent: float) -> float:
        """
        Calculate position size based on risk
        
        Args:
            symbol: Trading pair
            entry_price: Entry price
            risk_amount: Amount to risk in USDT
            stop_loss_percent: Stop loss distance as decimal (e.g., 0.02 for 2%)
            
        Returns:
            Position size (quantity)
        """
        try:
            # Get symbol info for precision
            info = self.get_symbol_info(symbol)
            if not info:
                return 0.0
            
            # Calculate quantity based on risk
            # Risk amount = Quantity * Entry price * Stop loss %
            quantity = risk_amount / (entry_price * stop_loss_percent)
            
            # Round to symbol's quantity step
            qty_step = info['qty_step']
            quantity = round(quantity / qty_step) * qty_step
            
            # Ensure within limits
            quantity = max(info['min_qty'], min(quantity, info['max_qty']))
            
            return quantity
        except Exception as e:
            log.error(f"Error calculating position size: {e}")
            return 0.0


if __name__ == "__main__":
    # Test the client
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ Please set BYBIT_API_KEY and BYBIT_API_SECRET in .env file")
        exit(1)
    
    print("🚀 Testing Bybit Demo Trading API...")
    client = BybitFuturesClient(api_key, api_secret, demo=True)
    
    print("\n📊 Account Balance:")
    balances = client.get_account_balance()
    for coin, balance in balances.items():
        print(f"  {coin}: {balance['wallet_balance']:.2f} USDT")
    
    print("\n💹 BTC Current Price:")
    btc_price = client.get_current_price('BTCUSDT')
    print(f"  BTCUSDT: ${btc_price:,.2f}")
    
    print("\n📈 Getting 15m klines...")
    klines = client.get_klines('BTCUSDT', '15m', limit=5)
    if klines:
        print(f"  Last 5 candles received")
        print(f"  Latest close: ${klines[-1]['close']:,.2f}")
    
    print("\n✅ Bybit client test complete!")
