"""
Signal Analyzer - Processes market data and generates trading signals
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from binance_client import BinanceFuturesClient
from strategies import get_strategy, calculate_stop_loss_take_profit
from logger import get_logger
import config

log = get_logger('SignalAnalyzer')


class SignalAnalyzer:
    """Analyzes market data and generates trading signals"""
    
    def __init__(self, binance_client: BinanceFuturesClient):
        """
        Initialize Signal Analyzer
        
        Args:
            binance_client: Binance Futures client instance
        """
        self.client = binance_client
    
    def prepare_dataframe(self, klines: List) -> pd.DataFrame:
        """
        Convert klines data to pandas DataFrame
        
        Args:
            klines: Raw klines data from Binance
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to appropriate types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            return df
            
        except Exception as e:
            log.error(f"Error preparing dataframe: {e}")
            return pd.DataFrame()
    
    def analyze_symbol(
        self,
        symbol: str,
        strategy_name: str,
        interval: str = config.DEFAULT_INTERVAL,
        limit: int = 500
    ) -> Optional[Dict]:
        """
        Analyze a symbol with specified strategy
        
        Args:
            symbol: Trading symbol
            strategy_name: Name of strategy to use
            interval: Candle interval
            limit: Number of candles to fetch
            
        Returns:
            Analysis result dictionary or None
        """
        try:
            # Get klines data
            klines = self.client.get_klines(symbol, interval, limit)
            if not klines:
                log.warning(f"No klines data for {symbol}")
                return None
            
            # Prepare DataFrame
            df = self.prepare_dataframe(klines)
            if df.empty:
                return None
            
            # Get strategy
            strategy = get_strategy(strategy_name)
            if not strategy:
                log.error(f"Strategy {strategy_name} not found")
                return None
            
            # Analyze
            result = strategy.analyze(df, symbol)
            
            # Add metadata
            result['symbol'] = symbol
            result['interval'] = interval
            result['timestamp'] = pd.Timestamp.now()
            
            return result
            
        except Exception as e:
            log.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def scan_multiple_symbols(
        self,
        symbols: List[str],
        strategy_name: str,
        interval: str = config.DEFAULT_INTERVAL,
        min_signal_strength: float = 50.0
    ) -> List[Dict]:
        """
        Scan multiple symbols for trading signals
        
        Args:
            symbols: List of symbols to scan
            strategy_name: Strategy to use
            interval: Candle interval
            min_signal_strength: Minimum signal strength to include
            
        Returns:
            List of signals that meet criteria
        """
        signals = []
        
        for symbol in symbols:
            try:
                result = self.analyze_symbol(symbol, strategy_name, interval)
                
                if result and result.get('signal') and result.get('strength', 0) >= min_signal_strength:
                    signals.append(result)
                    log.info(f"Signal found: {symbol} - {result['signal']} (Strength: {result['strength']})")
                    
            except Exception as e:
                log.error(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by signal strength
        signals.sort(key=lambda x: x.get('strength', 0), reverse=True)
        
        return signals
    
    def get_signal_with_levels(
        self,
        symbol: str,
        strategy_name: str,
        interval: str = config.DEFAULT_INTERVAL,
        leverage: int = config.DEFAULT_LEVERAGE,
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Get complete signal with entry, stop loss, and take profit levels
        
        Args:
            symbol: Trading symbol
            strategy_name: Strategy to use
            interval: Candle interval
            leverage: Leverage to use
            stop_loss_pct: Custom stop loss percentage
            take_profit_pct: Custom take profit percentage
            
        Returns:
            Complete signal dictionary
        """
        try:
            # Get basic signal
            signal = self.analyze_symbol(symbol, strategy_name, interval)
            
            if not signal or not signal.get('signal'):
                return None
            
            entry_price = signal['price']
            side = signal['signal']
            
            # Calculate SL/TP
            stop_loss, take_profit = calculate_stop_loss_take_profit(
                entry_price,
                side,
                stop_loss_pct,
                take_profit_pct
            )
            
            # Add trading levels
            signal['entry_price'] = entry_price
            signal['stop_loss'] = stop_loss
            signal['take_profit'] = take_profit
            signal['leverage'] = leverage
            signal['risk_reward_ratio'] = round(
                abs(take_profit - entry_price) / abs(entry_price - stop_loss),
                2
            )
            
            return signal
            
        except Exception as e:
            log.error(f"Error getting signal with levels for {symbol}: {e}")
            return None
    
    def get_market_overview(self, symbols: List[str]) -> Dict:
        """
        Get market overview for multiple symbols
        
        Args:
            symbols: List of symbols
            
        Returns:
            Market overview dictionary
        """
        overview = {
            'total_symbols': len(symbols),
            'bullish_count': 0,
            'bearish_count': 0,
            'neutral_count': 0,
            'symbols_data': []
        }
        
        for symbol in symbols:
            try:
                price = self.client.get_current_price(symbol)
                if price:
                    # Get simple trend using EMAs
                    klines = self.client.get_klines(symbol, '15m', 100)
                    df = self.prepare_dataframe(klines)
                    
                    if not df.empty:
                        from ta.trend import EMAIndicator
                        ema_9 = EMAIndicator(df['close'], window=9).ema_indicator().iloc[-1]
                        ema_21 = EMAIndicator(df['close'], window=21).ema_indicator().iloc[-1]
                        
                        if price > ema_9 > ema_21:
                            trend = 'BULLISH'
                            overview['bullish_count'] += 1
                        elif price < ema_9 < ema_21:
                            trend = 'BEARISH'
                            overview['bearish_count'] += 1
                        else:
                            trend = 'NEUTRAL'
                            overview['neutral_count'] += 1
                        
                        overview['symbols_data'].append({
                            'symbol': symbol,
                            'price': price,
                            'trend': trend
                        })
                        
            except Exception as e:
                log.error(f"Error getting overview for {symbol}: {e}")
                continue
        
        return overview
