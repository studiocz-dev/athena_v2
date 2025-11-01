"""
Trading Strategies with Technical Indicators
"""
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, MACD, SMAIndicator
from ta.momentum import RSIIndicator, StochRSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from typing import Dict, List, Tuple, Optional
from logger import get_logger
import config

log = get_logger('TradingStrategies')


class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
    
    def analyze(
        self,
        df: pd.DataFrame,
        symbol: str
    ) -> Dict:
        """
        Analyze market data and generate trading signal
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            
        Returns:
            Dictionary with signal information
        """
        raise NotImplementedError("Subclasses must implement analyze method")


class EMACrossStrategy(TradingStrategy):
    """EMA Crossover Strategy"""
    
    def __init__(self, fast_period: int = 9, slow_period: int = 21):
        super().__init__("EMA_CROSS")
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def analyze(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Generate signal based on EMA crossover"""
        try:
            # Calculate EMAs
            ema_fast = EMAIndicator(df['close'], window=self.fast_period).ema_indicator()
            ema_slow = EMAIndicator(df['close'], window=self.slow_period).ema_indicator()
            
            # Get recent values
            current_fast = ema_fast.iloc[-1]
            current_slow = ema_slow.iloc[-1]
            prev_fast = ema_fast.iloc[-2]
            prev_slow = ema_slow.iloc[-2]
            
            signal = None
            signal_strength = 0
            
            # Bullish crossover
            if prev_fast <= prev_slow and current_fast > current_slow:
                signal = 'LONG'
                signal_strength = min(abs(current_fast - current_slow) / current_slow * 100, 100)
            
            # Bearish crossover
            elif prev_fast >= prev_slow and current_fast < current_slow:
                signal = 'SHORT'
                signal_strength = min(abs(current_fast - current_slow) / current_slow * 100, 100)
            
            return {
                'signal': signal,
                'strength': round(signal_strength, 2),
                'price': df['close'].iloc[-1],
                'ema_fast': round(current_fast, 4),
                'ema_slow': round(current_slow, 4),
                'strategy': self.name
            }
            
        except Exception as e:
            log.error(f"Error in EMA Cross strategy: {e}")
            return {'signal': None, 'strength': 0, 'strategy': self.name}


class TripleEMAStrategy(TradingStrategy):
    """Triple EMA Strategy with trend confirmation"""
    
    def __init__(self, fast: int = 9, medium: int = 21, slow: int = 50):
        super().__init__("TRIPLE_EMA")
        self.fast = fast
        self.medium = medium
        self.slow = slow
    
    def analyze(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Generate signal based on triple EMA alignment"""
        try:
            # Calculate EMAs
            ema_fast = EMAIndicator(df['close'], window=self.fast).ema_indicator()
            ema_medium = EMAIndicator(df['close'], window=self.medium).ema_indicator()
            ema_slow = EMAIndicator(df['close'], window=self.slow).ema_indicator()
            
            # Current values
            curr_fast = ema_fast.iloc[-1]
            curr_medium = ema_medium.iloc[-1]
            curr_slow = ema_slow.iloc[-1]
            curr_price = df['close'].iloc[-1]
            
            # Previous values
            prev_fast = ema_fast.iloc[-2]
            prev_medium = ema_medium.iloc[-2]
            
            signal = None
            signal_strength = 0
            
            # Strong bullish: All EMAs aligned + price crossing above fast EMA
            if curr_fast > curr_medium > curr_slow:
                if prev_fast <= prev_medium and curr_fast > curr_medium:
                    signal = 'LONG'
                    signal_strength = 80
            
            # Strong bearish: All EMAs aligned + price crossing below fast EMA
            elif curr_fast < curr_medium < curr_slow:
                if prev_fast >= prev_medium and curr_fast < curr_medium:
                    signal = 'SHORT'
                    signal_strength = 80
            
            return {
                'signal': signal,
                'strength': signal_strength,
                'price': curr_price,
                'ema_fast': round(curr_fast, 4),
                'ema_medium': round(curr_medium, 4),
                'ema_slow': round(curr_slow, 4),
                'strategy': self.name
            }
            
        except Exception as e:
            log.error(f"Error in Triple EMA strategy: {e}")
            return {'signal': None, 'strength': 0, 'strategy': self.name}


class RSIDivergenceStrategy(TradingStrategy):
    """RSI with Divergence Detection"""
    
    def __init__(self, rsi_period: int = 14):
        super().__init__("RSI_DIVERGENCE")
        self.rsi_period = rsi_period
    
    def analyze(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Generate signal based on RSI levels and divergences"""
        try:
            # Calculate RSI
            rsi = RSIIndicator(df['close'], window=self.rsi_period).rsi()
            
            current_rsi = rsi.iloc[-1]
            current_price = df['close'].iloc[-1]
            
            signal = None
            signal_strength = 0
            
            # Oversold condition
            if current_rsi < config.RSI_OVERSOLD:
                signal = 'LONG'
                signal_strength = (config.RSI_OVERSOLD - current_rsi) / config.RSI_OVERSOLD * 100
            
            # Overbought condition
            elif current_rsi > config.RSI_OVERBOUGHT:
                signal = 'SHORT'
                signal_strength = (current_rsi - config.RSI_OVERBOUGHT) / (100 - config.RSI_OVERBOUGHT) * 100
            
            return {
                'signal': signal,
                'strength': round(min(signal_strength, 100), 2),
                'price': current_price,
                'rsi': round(current_rsi, 2),
                'strategy': self.name
            }
            
        except Exception as e:
            log.error(f"Error in RSI Divergence strategy: {e}")
            return {'signal': None, 'strength': 0, 'strategy': self.name}


class MACDStrategy(TradingStrategy):
    """MACD Signal Strategy"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__("MACD_SIGNAL")
        self.fast = fast
        self.slow = slow
        self.signal_period = signal
    
    def analyze(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Generate signal based on MACD crossover"""
        try:
            # Calculate MACD
            macd_indicator = MACD(
                df['close'],
                window_fast=self.fast,
                window_slow=self.slow,
                window_sign=self.signal_period
            )
            
            macd_line = macd_indicator.macd()
            signal_line = macd_indicator.macd_signal()
            histogram = macd_indicator.macd_diff()
            
            # Current values
            curr_macd = macd_line.iloc[-1]
            curr_signal = signal_line.iloc[-1]
            curr_hist = histogram.iloc[-1]
            
            # Previous values
            prev_macd = macd_line.iloc[-2]
            prev_signal = signal_line.iloc[-2]
            
            signal = None
            signal_strength = 0
            
            # Bullish crossover
            if prev_macd <= prev_signal and curr_macd > curr_signal:
                signal = 'LONG'
                signal_strength = min(abs(curr_hist) * 10, 100)
            
            # Bearish crossover
            elif prev_macd >= prev_signal and curr_macd < curr_signal:
                signal = 'SHORT'
                signal_strength = min(abs(curr_hist) * 10, 100)
            
            return {
                'signal': signal,
                'strength': round(signal_strength, 2),
                'price': df['close'].iloc[-1],
                'macd': round(curr_macd, 4),
                'signal_line': round(curr_signal, 4),
                'histogram': round(curr_hist, 4),
                'strategy': self.name
            }
            
        except Exception as e:
            log.error(f"Error in MACD strategy: {e}")
            return {'signal': None, 'strength': 0, 'strategy': self.name}


class StochRSIStrategy(TradingStrategy):
    """Stochastic RSI Strategy"""
    
    def __init__(self, period: int = 14, smooth1: int = 3, smooth2: int = 3):
        super().__init__("STOCH_RSI")
        self.period = period
        self.smooth1 = smooth1
        self.smooth2 = smooth2
    
    def analyze(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Generate signal based on Stochastic RSI"""
        try:
            # Calculate Stochastic RSI
            stoch_rsi = StochRSIIndicator(
                df['close'],
                window=self.period,
                smooth1=self.smooth1,
                smooth2=self.smooth2
            )
            
            stoch_k = stoch_rsi.stochrsi_k() * 100
            stoch_d = stoch_rsi.stochrsi_d() * 100
            
            curr_k = stoch_k.iloc[-1]
            curr_d = stoch_d.iloc[-1]
            prev_k = stoch_k.iloc[-2]
            prev_d = stoch_d.iloc[-2]
            
            signal = None
            signal_strength = 0
            
            # Oversold crossover
            if curr_k < config.STOCH_OVERSOLD and curr_d < config.STOCH_OVERSOLD:
                if prev_k <= prev_d and curr_k > curr_d:
                    signal = 'LONG'
                    signal_strength = (config.STOCH_OVERSOLD - curr_k) / config.STOCH_OVERSOLD * 100
            
            # Overbought crossover
            elif curr_k > config.STOCH_OVERBOUGHT and curr_d > config.STOCH_OVERBOUGHT:
                if prev_k >= prev_d and curr_k < curr_d:
                    signal = 'SHORT'
                    signal_strength = (curr_k - config.STOCH_OVERBOUGHT) / (100 - config.STOCH_OVERBOUGHT) * 100
            
            return {
                'signal': signal,
                'strength': round(min(signal_strength, 100), 2),
                'price': df['close'].iloc[-1],
                'stoch_k': round(curr_k, 2),
                'stoch_d': round(curr_d, 2),
                'strategy': self.name
            }
            
        except Exception as e:
            log.error(f"Error in Stoch RSI strategy: {e}")
            return {'signal': None, 'strength': 0, 'strategy': self.name}


class BreakoutStrategy(TradingStrategy):
    """Breakout Strategy with Volume Confirmation"""
    
    def __init__(self, lookback: int = 20):
        super().__init__("BREAKOUT")
        self.lookback = lookback
    
    def analyze(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Generate signal based on price breakouts"""
        try:
            # Calculate resistance and support levels
            resistance = df['high'].rolling(window=self.lookback).max()
            support = df['low'].rolling(window=self.lookback).min()
            
            # Volume analysis
            avg_volume = df['volume'].rolling(window=self.lookback).mean()
            
            curr_price = df['close'].iloc[-1]
            curr_high = df['high'].iloc[-1]
            curr_low = df['low'].iloc[-1]
            curr_volume = df['volume'].iloc[-1]
            
            prev_resistance = resistance.iloc[-2]
            prev_support = support.iloc[-2]
            avg_vol = avg_volume.iloc[-1]
            
            signal = None
            signal_strength = 0
            
            # Breakout above resistance with high volume
            if curr_high > prev_resistance and curr_volume > avg_vol * 1.5:
                signal = 'LONG'
                breakout_pct = (curr_high - prev_resistance) / prev_resistance * 100
                volume_multiplier = curr_volume / avg_vol
                signal_strength = min(breakout_pct * volume_multiplier * 10, 100)
            
            # Breakdown below support with high volume
            elif curr_low < prev_support and curr_volume > avg_vol * 1.5:
                signal = 'SHORT'
                breakdown_pct = (prev_support - curr_low) / prev_support * 100
                volume_multiplier = curr_volume / avg_vol
                signal_strength = min(breakdown_pct * volume_multiplier * 10, 100)
            
            return {
                'signal': signal,
                'strength': round(signal_strength, 2),
                'price': curr_price,
                'resistance': round(prev_resistance, 4),
                'support': round(prev_support, 4),
                'volume_ratio': round(curr_volume / avg_vol, 2) if avg_vol > 0 else 0,
                'strategy': self.name
            }
            
        except Exception as e:
            log.error(f"Error in Breakout strategy: {e}")
            return {'signal': None, 'strength': 0, 'strategy': self.name}


class SupportResistanceStrategy(TradingStrategy):
    """Support and Resistance Strategy"""
    
    def __init__(self, lookback: int = 50):
        super().__init__("SUPPORT_RESISTANCE")
        self.lookback = lookback
    
    def find_levels(self, df: pd.DataFrame) -> Tuple[List[float], List[float]]:
        """Find support and resistance levels"""
        highs = df['high'].values
        lows = df['low'].values
        
        resistance_levels = []
        support_levels = []
        
        # Find local maxima and minima
        for i in range(2, len(highs) - 2):
            # Resistance (local high)
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                resistance_levels.append(highs[i])
            
            # Support (local low)
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                support_levels.append(lows[i])
        
        return support_levels, resistance_levels
    
    def analyze(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Generate signal based on support/resistance bounce"""
        try:
            # Get recent data
            recent_df = df.tail(self.lookback)
            
            # Find S/R levels
            support_levels, resistance_levels = self.find_levels(recent_df)
            
            curr_price = df['close'].iloc[-1]
            prev_close = df['close'].iloc[-2]
            
            signal = None
            signal_strength = 0
            nearest_support = None
            nearest_resistance = None
            
            # Find nearest levels
            if support_levels:
                nearest_support = max([s for s in support_levels if s < curr_price], default=None)
            
            if resistance_levels:
                nearest_resistance = min([r for r in resistance_levels if r > curr_price], default=None)
            
            # Bounce off support
            if nearest_support and abs(curr_price - nearest_support) / nearest_support < 0.01:
                if prev_close < nearest_support and curr_price >= nearest_support:
                    signal = 'LONG'
                    signal_strength = 70
            
            # Bounce off resistance
            elif nearest_resistance and abs(curr_price - nearest_resistance) / nearest_resistance < 0.01:
                if prev_close > nearest_resistance and curr_price <= nearest_resistance:
                    signal = 'SHORT'
                    signal_strength = 70
            
            return {
                'signal': signal,
                'strength': signal_strength,
                'price': curr_price,
                'nearest_support': round(nearest_support, 4) if nearest_support else None,
                'nearest_resistance': round(nearest_resistance, 4) if nearest_resistance else None,
                'strategy': self.name
            }
            
        except Exception as e:
            log.error(f"Error in Support/Resistance strategy: {e}")
            return {'signal': None, 'strength': 0, 'strategy': self.name}


def get_strategy(strategy_name: str) -> Optional[TradingStrategy]:
    """
    Get strategy instance by name
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        Strategy instance or None
    """
    strategies = {
        'EMA_CROSS': EMACrossStrategy(),
        'TRIPLE_EMA': TripleEMAStrategy(),
        'RSI_DIVERGENCE': RSIDivergenceStrategy(),
        'MACD_SIGNAL': MACDStrategy(),
        'STOCH_RSI': StochRSIStrategy(),
        'BREAKOUT': BreakoutStrategy(),
        'SUPPORT_RESISTANCE': SupportResistanceStrategy()
    }
    
    return strategies.get(strategy_name)


def calculate_stop_loss_take_profit(
    entry_price: float,
    side: str,
    stop_loss_pct: float = None,
    take_profit_pct: float = None
) -> Tuple[float, float]:
    """
    Calculate stop loss and take profit prices
    
    Args:
        entry_price: Entry price
        side: 'LONG' or 'SHORT'
        stop_loss_pct: Stop loss percentage (default from config)
        take_profit_pct: Take profit percentage (default from config)
        
    Returns:
        Tuple of (stop_loss_price, take_profit_price)
    """
    if stop_loss_pct is None:
        stop_loss_pct = config.DEFAULT_STOP_LOSS_PERCENTAGE
    
    if take_profit_pct is None:
        take_profit_pct = config.DEFAULT_TAKE_PROFIT_PERCENTAGE
    
    if side == 'LONG':
        stop_loss = entry_price * (1 - stop_loss_pct / 100)
        take_profit = entry_price * (1 + take_profit_pct / 100)
    else:  # SHORT
        stop_loss = entry_price * (1 + stop_loss_pct / 100)
        take_profit = entry_price * (1 - take_profit_pct / 100)
    
    return round(stop_loss, 4), round(take_profit, 4)
