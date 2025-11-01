"""
Binance Futures Trading Client
Handles API interactions with Binance Futures
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.enums import *
from typing import Dict, List, Optional, Tuple
import asyncio
from logger import get_logger
import config

log = get_logger('BinanceClient')


class BinanceFuturesClient:
    """Wrapper for Binance Futures API with safety features"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize Binance Futures client
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet if True
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Initialize client with time synchronization
        if testnet:
            self.client = Client(api_key, api_secret, testnet=True)
            # Get server time and sync
            try:
                server_time = self.client.get_server_time()
                import time
                time_offset = server_time['serverTime'] - int(time.time() * 1000)
                self.client.timestamp_offset = time_offset
            except:
                pass
            log.info("Connected to Binance Futures TESTNET")
        else:
            self.client = Client(api_key, api_secret)
            # Get server time and sync
            try:
                server_time = self.client.get_server_time()
                import time
                time_offset = server_time['serverTime'] - int(time.time() * 1000)
                self.client.timestamp_offset = time_offset
            except:
                pass
            log.info("Connected to Binance Futures MAINNET")
    
    def get_account_balance(self) -> Dict:
        """Get futures account balance"""
        try:
            account = self.client.futures_account()
            balances = {}
            for asset in account['assets']:
                if float(asset['walletBalance']) > 0:
                    balances[asset['asset']] = {
                        'wallet_balance': float(asset['walletBalance']),
                        'unrealized_pnl': float(asset['unrealizedProfit']),
                        'available_balance': float(asset['availableBalance'])
                    }
            return balances
        except BinanceAPIException as e:
            log.error(f"Error getting account balance: {e}")
            return {}
    
    def get_position_info(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open positions
        
        Args:
            symbol: Specific symbol to query, or None for all positions
            
        Returns:
            List of position dictionaries
        """
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            open_positions = []
            
            for pos in positions:
                position_amt = float(pos.get('positionAmt', 0))
                if position_amt != 0:
                    open_positions.append({
                        'symbol': pos['symbol'],
                        'position_amount': position_amt,
                        'entry_price': float(pos.get('entryPrice', 0)),
                        'mark_price': float(pos.get('markPrice', 0)),
                        'unrealized_pnl': float(pos.get('unRealizedProfit', 0)),
                        'leverage': int(pos.get('leverage', 1)),
                        'liquidation_price': float(pos.get('liquidationPrice', 0)) if pos.get('liquidationPrice') else 0,
                        'side': 'LONG' if position_amt > 0 else 'SHORT'
                    })
            
            return open_positions
        except BinanceAPIException as e:
            log.error(f"Error getting position info: {e}")
            return []
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """
        Set leverage for a symbol
        
        Args:
            symbol: Trading symbol
            leverage: Leverage value (1-125)
            
        Returns:
            True if successful
        """
        try:
            self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
            log.info(f"Set leverage to {leverage}x for {symbol}")
            return True
        except BinanceAPIException as e:
            log.error(f"Error setting leverage for {symbol}: {e}")
            return False
    
    def set_margin_type(self, symbol: str, margin_type: str = 'CROSSED') -> bool:
        """
        Set margin type (ISOLATED or CROSSED)
        
        Args:
            symbol: Trading symbol
            margin_type: 'ISOLATED' or 'CROSSED'
            
        Returns:
            True if successful
        """
        try:
            self.client.futures_change_margin_type(symbol=symbol, marginType=margin_type)
            log.info(f"Set margin type to {margin_type} for {symbol}")
            return True
        except BinanceAPIException as e:
            # Margin type might already be set
            if "No need to change margin type" in str(e):
                log.debug(f"Margin type already set to {margin_type} for {symbol}")
                return True
            log.error(f"Error setting margin type for {symbol}: {e}")
            return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol trading information"""
        try:
            exchange_info = self.client.futures_exchange_info()
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    return {
                        'symbol': s['symbol'],
                        'status': s['status'],
                        'base_asset': s['baseAsset'],
                        'quote_asset': s['quoteAsset'],
                        'price_precision': s['pricePrecision'],
                        'quantity_precision': s['quantityPrecision'],
                        'min_qty': float([f['minQty'] for f in s['filters'] if f['filterType'] == 'LOT_SIZE'][0]),
                        'max_qty': float([f['maxQty'] for f in s['filters'] if f['filterType'] == 'LOT_SIZE'][0]),
                        'step_size': float([f['stepSize'] for f in s['filters'] if f['filterType'] == 'LOT_SIZE'][0]),
                        'tick_size': float([f['tickSize'] for f in s['filters'] if f['filterType'] == 'PRICE_FILTER'][0])
                    }
            return None
        except BinanceAPIException as e:
            log.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for symbol"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            log.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List]:
        """
        Get candlestick data
        
        Args:
            symbol: Trading symbol
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of candles to fetch (max 1500)
            
        Returns:
            List of kline data
        """
        try:
            klines = self.client.futures_klines(symbol=symbol, interval=interval, limit=limit)
            return klines
        except BinanceAPIException as e:
            log.error(f"Error getting klines for {symbol}: {e}")
            return []
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        reduce_only: bool = False
    ) -> Optional[Dict]:
        """
        Place a market order
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            reduce_only: True to only reduce position
            
        Returns:
            Order response dict or None
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=FUTURE_ORDER_TYPE_MARKET,
                quantity=quantity,
                reduceOnly=reduce_only
            )
            log.info(f"Market order placed: {symbol} {side} {quantity}")
            return order
        except BinanceAPIException as e:
            log.error(f"Error placing market order: {e}")
            return None
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = TIME_IN_FORCE_GTC
    ) -> Optional[Dict]:
        """
        Place a limit order
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (GTC, IOC, FOK)
            
        Returns:
            Order response dict or None
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=FUTURE_ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=price,
                timeInForce=time_in_force
            )
            log.info(f"Limit order placed: {symbol} {side} {quantity} @ {price}")
            return order
        except BinanceAPIException as e:
            log.error(f"Error placing limit order: {e}")
            return None
    
    def place_stop_loss(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float
    ) -> Optional[Dict]:
        """
        Place a stop-loss market order
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL' (opposite of position)
            quantity: Order quantity
            stop_price: Stop trigger price
            
        Returns:
            Order response dict or None
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=FUTURE_ORDER_TYPE_STOP_MARKET,
                quantity=quantity,
                stopPrice=stop_price,
                reduceOnly=True
            )
            log.info(f"Stop-loss order placed: {symbol} {side} {quantity} @ {stop_price}")
            return order
        except BinanceAPIException as e:
            log.error(f"Error placing stop-loss order: {e}")
            return None
    
    def place_take_profit(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float
    ) -> Optional[Dict]:
        """
        Place a take-profit market order
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL' (opposite of position)
            quantity: Order quantity
            stop_price: Take-profit trigger price
            
        Returns:
            Order response dict or None
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET,
                quantity=quantity,
                stopPrice=stop_price,
                reduceOnly=True
            )
            log.info(f"Take-profit order placed: {symbol} {side} {quantity} @ {stop_price}")
            return order
        except BinanceAPIException as e:
            log.error(f"Error placing take-profit order: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """Cancel an open order"""
        try:
            self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            log.info(f"Order {order_id} cancelled for {symbol}")
            return True
        except BinanceAPIException as e:
            log.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def cancel_all_orders(self, symbol: str) -> bool:
        """Cancel all open orders for a symbol"""
        try:
            self.client.futures_cancel_all_open_orders(symbol=symbol)
            log.info(f"All orders cancelled for {symbol}")
            return True
        except BinanceAPIException as e:
            log.error(f"Error cancelling all orders for {symbol}: {e}")
            return False
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open orders"""
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            return orders
        except BinanceAPIException as e:
            log.error(f"Error getting open orders: {e}")
            return []
    
    def close_position(self, symbol: str) -> bool:
        """
        Close an open position completely
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if successful
        """
        try:
            # Get current position
            positions = self.get_position_info(symbol)
            if not positions:
                log.warning(f"No open position found for {symbol}")
                return False
            
            position = positions[0]
            position_amt = abs(position['position_amount'])
            
            # Determine side for closing (opposite of position)
            close_side = SIDE_SELL if position['side'] == 'LONG' else SIDE_BUY
            
            # Cancel all existing orders first
            self.cancel_all_orders(symbol)
            
            # Place market order to close
            order = self.place_market_order(symbol, close_side, position_amt, reduce_only=True)
            
            if order:
                log.info(f"Position closed for {symbol}")
                return True
            return False
            
        except Exception as e:
            log.error(f"Error closing position for {symbol}: {e}")
            return False
    
    def calculate_quantity(
        self,
        symbol: str,
        usdt_amount: float,
        leverage: int,
        price: Optional[float] = None
    ) -> Tuple[float, Dict]:
        """
        Calculate order quantity based on USDT amount and leverage
        
        Args:
            symbol: Trading symbol
            usdt_amount: Amount in USDT to trade
            leverage: Leverage multiplier
            price: Price to use (if None, uses current market price)
            
        Returns:
            Tuple of (quantity, symbol_info)
        """
        try:
            # Get symbol info
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                return 0, {}
            
            # Get current price if not provided
            if price is None:
                price = self.get_current_price(symbol)
                if price is None:
                    return 0, symbol_info
            
            # Calculate quantity
            notional_value = usdt_amount * leverage
            quantity = notional_value / price
            
            # Round to step size
            step_size = symbol_info['step_size']
            quantity = round(quantity / step_size) * step_size
            
            # Apply precision
            precision = symbol_info['quantity_precision']
            quantity = round(quantity, precision)
            
            # Check min/max constraints
            if quantity < symbol_info['min_qty']:
                log.warning(f"Calculated quantity {quantity} is below minimum {symbol_info['min_qty']}")
                return 0, symbol_info
            
            if quantity > symbol_info['max_qty']:
                log.warning(f"Calculated quantity {quantity} exceeds maximum {symbol_info['max_qty']}")
                quantity = symbol_info['max_qty']
            
            return quantity, symbol_info
            
        except Exception as e:
            log.error(f"Error calculating quantity: {e}")
            return 0, {}
