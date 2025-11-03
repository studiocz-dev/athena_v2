"""
Gate.io Futures Testnet Client
Handles all Gate.io futures API interactions for testnet trading
"""

import time
import hmac
import hashlib
from typing import Dict, List, Optional, Tuple
import requests
from datetime import datetime

class GateClient:
    """Client for Gate.io Futures Testnet API"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize Gate.io client
        
        Args:
            api_key: Gate.io API key
            api_secret: Gate.io API secret
            testnet: Use testnet endpoint (default True)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Use testnet endpoint
        if testnet:
            self.base_url = "https://api-testnet.gateapi.io/api/v4"
        else:
            self.base_url = "https://api.gateio.ws/api/v4"
        
        self.settle = "usdt"  # Settlement currency (USDT futures)
        
        print(f"[GATE] Initialized Gate.io client - Testnet: {testnet}")
    
    def _generate_signature(self, method: str, url_path: str, query_string: str = "", body: str = "") -> Dict[str, str]:
        """
        Generate Gate.io API signature
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            url_path: API endpoint path
            query_string: Query parameters string
            body: Request body
            
        Returns:
            Headers with signature
        """
        t = str(int(time.time()))
        
        # Hash the body with SHA512
        m = hashlib.sha512()
        m.update((body or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        
        # Create signature string
        s = f'{method}\n{url_path}\n{query_string or ""}\n{hashed_payload}\n{t}'
        
        # Sign with HMAC SHA512
        sign = hmac.new(
            self.api_secret.encode('utf-8'),
            s.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        return {
            'KEY': self.api_key,
            'Timestamp': t,
            'SIGN': sign
        }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                      data: Optional[Dict] = None, signed: bool = True) -> Dict:
        """
        Make API request to Gate.io
        
        Args:
            method: HTTP method
            endpoint: API endpoint (e.g., '/futures/usdt/contracts')
            params: Query parameters
            data: Request body data
            signed: Whether to sign the request
            
        Returns:
            API response as dict
        """
        url = self.base_url + endpoint
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Build query string
        query_string = ""
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        
        # Build request body
        body = ""
        if data:
            import json
            body = json.dumps(data)
        
        # Add signature if required
        if signed:
            # Extract path from full endpoint
            path = endpoint
            sign_headers = self._generate_signature(method, path, query_string, body)
            headers.update(sign_headers)
        
        # Make request
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, params=params, data=body, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Gate.io API Error: {e}"
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data.get('label', '')}: {error_data.get('message', '')}"
            except:
                pass
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Gate.io Request Error: {str(e)}")
    
    # ==================== Market Data Methods ====================
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT' -> 'BTC_USDT')
            
        Returns:
            Current price as float
        """
        # Convert BTCUSDT to BTC_USDT format
        contract = self._format_symbol(symbol)
        
        endpoint = f"/futures/{self.settle}/tickers"
        params = {"contract": contract}
        
        response = self._make_request("GET", endpoint, params=params, signed=False)
        
        if response and len(response) > 0:
            return float(response[0]['last'])
        
        raise Exception(f"Could not get price for {symbol}")
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[List]:
        """
        Get candlestick/kline data
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
            limit: Number of candles (default 100, max depends on timeframe)
            
        Returns:
            List of OHLCV candles: [[timestamp, open, high, low, close, volume], ...]
        """
        contract = self._format_symbol(symbol)
        
        # Map interval formats
        interval_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d'
        }
        
        gate_interval = interval_map.get(interval, '1h')
        
        endpoint = f"/futures/{self.settle}/candlesticks"
        params = {
            "contract": contract,
            "interval": gate_interval,
            "limit": limit
        }
        
        response = self._make_request("GET", endpoint, params=params, signed=False)
        
        # Convert Gate.io format to standard OHLCV
        # Gate format: {t: timestamp, o: open, h: high, l: low, c: close, v: volume}
        candles = []
        for candle in response:
            candles.append([
                int(candle['t']),           # timestamp (seconds)
                float(candle['o']),         # open
                float(candle['h']),         # high
                float(candle['l']),         # low
                float(candle['c']),         # close
                float(candle.get('v', 0))   # volume
            ])
        
        return candles
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Get trading rules and info for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            Symbol information dict
        """
        contract = self._format_symbol(symbol)
        
        endpoint = f"/futures/{self.settle}/contracts/{contract}"
        
        response = self._make_request("GET", endpoint, signed=False)
        
        return {
            'symbol': symbol,
            'contract': response['name'],
            'price_precision': int(response.get('order_price_round', 2)),
            'quantity_precision': 0,  # Gate uses contracts, not decimals
            'min_notional': float(response.get('order_size_min', 1)),
            'min_qty': float(response.get('order_size_min', 1)),
            'leverage_max': float(response.get('leverage_max', 100))
        }
    
    # ==================== Account Methods ====================
    
    def get_account_balance(self) -> Dict:
        """
        Get futures account balance
        
        Returns:
            Account balance info including total, available, unrealized PNL
        """
        endpoint = f"/futures/{self.settle}/accounts"
        
        response = self._make_request("GET", endpoint)
        
        return {
            'total': float(response.get('total', 0)),
            'available': float(response.get('available', 0)),
            'unrealized_pnl': float(response.get('unrealised_pnl', 0)),
            'position_margin': float(response.get('position_margin', 0)),
            'order_margin': float(response.get('order_margin', 0)),
            'currency': response.get('currency', 'USDT')
        }
    
    def get_position_info(self, symbol: str) -> Optional[Dict]:
        """
        Get position information for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            
        Returns:
            Position info dict or None if no position
        """
        contract = self._format_symbol(symbol)
        
        endpoint = f"/futures/{self.settle}/positions/{contract}"
        
        try:
            response = self._make_request("GET", endpoint)
            
            size = int(response.get('size', 0))
            if size == 0:
                return None
            
            return {
                'symbol': symbol,
                'size': size,
                'leverage': float(response.get('leverage', 0)),
                'entry_price': float(response.get('entry_price', 0)),
                'mark_price': float(response.get('mark_price', 0)),
                'liquidation_price': float(response.get('liq_price', 0)),
                'unrealized_pnl': float(response.get('unrealised_pnl', 0)),
                'margin': float(response.get('margin', 0)),
                'side': 'long' if size > 0 else 'short'
            }
        except:
            return None
    
    # ==================== Trading Methods ====================
    
    def place_order(self, symbol: str, side: str, quantity: float, 
                    price: Optional[float] = None, reduce_only: bool = False) -> Dict:
        """
        Place a futures order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'buy' or 'sell'
            quantity: Order quantity (number of contracts)
            price: Limit price (None for market order)
            reduce_only: Whether order can only reduce position
            
        Returns:
            Order information dict
        """
        contract = self._format_symbol(symbol)
        
        # Gate.io uses positive for long, negative for short
        size = int(abs(quantity))
        if side.lower() == 'sell':
            size = -size
        
        order_data = {
            'contract': contract,
            'size': size,
            'tif': 'ioc' if price is None else 'gtc',  # IOC for market, GTC for limit
            'text': 'athena_bot'
        }
        
        # Add price for limit orders
        if price is not None:
            order_data['price'] = str(price)
        else:
            order_data['price'] = '0'  # Market order
        
        # Reduce-only flag
        if reduce_only:
            order_data['close'] = True
        
        endpoint = f"/futures/{self.settle}/orders"
        
        response = self._make_request("POST", endpoint, data=order_data)
        
        return {
            'order_id': str(response['id']),
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': float(response.get('price', 0)),
            'status': response.get('status', 'unknown'),
            'timestamp': response.get('create_time', 0)
        }
    
    def close_position(self, symbol: str, side: str) -> Dict:
        """
        Close an open position
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: Position side to close ('long' or 'short')
            
        Returns:
            Close order information
        """
        # Get current position
        position = self.get_position_info(symbol)
        if not position:
            return {'success': False, 'message': 'No position to close'}
        
        # Determine close side (opposite of position)
        close_side = 'sell' if position['side'] == 'long' else 'buy'
        quantity = abs(position['size'])
        
        # Place reduce-only market order
        return self.place_order(symbol, close_side, quantity, reduce_only=True)
    
    def set_leverage(self, symbol: str, leverage: int) -> Dict:
        """
        Set leverage for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            leverage: Leverage value (1-125 depending on symbol)
            
        Returns:
            Updated position info
        """
        contract = self._format_symbol(symbol)
        
        endpoint = f"/futures/{self.settle}/positions/{contract}/leverage"
        params = {'leverage': leverage}
        
        response = self._make_request("POST", endpoint, params=params)
        
        return {
            'symbol': symbol,
            'leverage': float(response.get('leverage', leverage)),
            'success': True
        }
    
    def cancel_all_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Cancel all open orders
        
        Args:
            symbol: Trading pair (optional, cancels all if None)
            
        Returns:
            List of cancelled orders
        """
        params = {}
        if symbol:
            params['contract'] = self._format_symbol(symbol)
        
        endpoint = f"/futures/{self.settle}/orders"
        
        response = self._make_request("DELETE", endpoint, params=params)
        
        return response
    
    # ==================== Helper Methods ====================
    
    def _format_symbol(self, symbol: str) -> str:
        """
        Convert symbol from exchange format to Gate.io format
        
        Args:
            symbol: Symbol in format 'BTCUSDT'
            
        Returns:
            Gate.io contract format 'BTC_USDT'
        """
        # Remove 'USDT' and add underscore
        if symbol.endswith('USDT'):
            base = symbol[:-4]
            return f"{base}_USDT"
        
        return symbol
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test API connection and credentials
        
        Returns:
            (success: bool, message: str)
        """
        try:
            # Test public endpoint
            endpoint = f"/futures/{self.settle}/contracts"
            contracts = self._make_request("GET", endpoint, signed=False)
            
            if not contracts or len(contracts) == 0:
                return False, "No contracts returned from API"
            
            print(f"✅ Public API working - {len(contracts)} contracts available")
            
            # Test private endpoint
            balance = self.get_account_balance()
            print(f"✅ Private API working - Balance: {balance['total']} USDT")
            
            return True, f"Connection successful! Balance: {balance['total']} USDT"
            
        except Exception as e:
            return False, f"Connection failed: {str(e)}"


# Convenience function for quick testing
def test_gate_client(api_key: str, api_secret: str):
    """
    Quick test of Gate.io client
    
    Args:
        api_key: Gate.io API key
        api_secret: Gate.io API secret
    """
    print("=" * 60)
    print("Testing Gate.io Testnet Client")
    print("=" * 60)
    
    client = GateClient(api_key, api_secret, testnet=True)
    
    # Test connection
    success, message = client.test_connection()
    print(f"\n{'✅' if success else '❌'} {message}")
    
    if success:
        # Test market data
        print("\n" + "=" * 60)
        print("Testing Market Data")
        print("=" * 60)
        
        try:
            price = client.get_current_price('BTCUSDT')
            print(f"✅ BTC Price: ${price:,.2f}")
            
            klines = client.get_klines('BTCUSDT', '1h', limit=5)
            print(f"✅ Klines: Retrieved {len(klines)} candles")
            print(f"   Latest: Open ${klines[-1][1]:,.2f}, Close ${klines[-1][4]:,.2f}")
            
            info = client.get_symbol_info('BTCUSDT')
            print(f"✅ Symbol Info: Max Leverage {info['leverage_max']}x")
            
        except Exception as e:
            print(f"❌ Market data error: {e}")
        
        # Test position info
        print("\n" + "=" * 60)
        print("Testing Position Info")
        print("=" * 60)
        
        try:
            position = client.get_position_info('BTCUSDT')
            if position:
                print(f"✅ Active Position: {position['side'].upper()} {position['size']} contracts")
            else:
                print("✅ No active position")
        except Exception as e:
            print(f"❌ Position info error: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('GATE_API_KEY')
    api_secret = os.getenv('GATE_API_SECRET')
    
    if api_key and api_secret:
        test_gate_client(api_key, api_secret)
    else:
        print("❌ Please set GATE_API_KEY and GATE_API_SECRET in .env file")
