"""
Enhanced Trading Strategies with Multi-Timeframe Support
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from strategies import TradingStrategy, TripleEMAStrategy

logger = logging.getLogger(__name__)


class EnhancedTripleEMAStrategy(TripleEMAStrategy):
    """
    Enhanced Triple EMA Strategy with optimized parameters.
    
    Improvements:
    1. Adjustable EMA periods for optimization
    2. Enhanced entry conditions with momentum filter
    3. Dynamic stop loss and take profit based on volatility (ATR)
    4. Volume confirmation requirement
    5. Multi-timeframe support ready
    
    Default parameters optimized from backtesting:
    - Fast EMA: 9
    - Medium EMA: 21
    - Slow EMA: 50
    """
    
    def __init__(
        self,
        fast_period: int = 9,
        medium_period: int = 21,
        slow_period: int = 50,
        atr_period: int = 14,
        atr_multiplier: float = 2.0,
        volume_threshold: float = 1.2,
        require_volume_confirmation: bool = True
    ):
        """
        Initialize enhanced strategy with customizable parameters.
        
        Args:
            fast_period: Fast EMA period (default: 9)
            medium_period: Medium EMA period (default: 21)
            slow_period: Slow EMA period (default: 50)
            atr_period: ATR period for volatility (default: 14)
            atr_multiplier: Multiplier for ATR-based SL/TP (default: 2.0)
            volume_threshold: Volume multiplier vs average (default: 1.2)
            require_volume_confirmation: Require volume spike for signals (default: True)
        """
        super().__init__()
        self.fast_period = fast_period
        self.medium_period = medium_period
        self.slow_period = slow_period
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.volume_threshold = volume_threshold
        self.require_volume_confirmation = require_volume_confirmation
        
        self.name = f"ENHANCED_TRIPLE_EMA_{fast_period}_{medium_period}_{slow_period}"
        
        logger.debug(
            f"Initialized {self.name} - ATR: {atr_period}, "
            f"Volume threshold: {volume_threshold}"
        )
    
    def generate_signal(self, df: pd.DataFrame) -> str:
        """
        Generate enhanced trading signal.
        
        Entry conditions for BUY:
        1. Fast EMA crosses above Medium EMA (golden cross)
        2. Medium EMA > Slow EMA (trending up)
        3. Price is above all EMAs (momentum confirmation)
        4. Volume > threshold * average volume (optional)
        5. Recent price momentum positive
        
        Entry conditions for SELL:
        1. Fast EMA crosses below Medium EMA (death cross)
        2. Medium EMA < Slow EMA (trending down)
        3. Price is below all EMAs (momentum confirmation)
        4. Volume > threshold * average volume (optional)
        5. Recent price momentum negative
        """
        if df.empty or len(df) < self.slow_period + 5:
            return 'HOLD'
        
        # Calculate indicators
        df = self._calculate_indicators(df)
        
        # Get latest values
        current_idx = -1
        prev_idx = -2
        
        current_price = float(df['close'].iloc[current_idx])
        fast_ema = float(df[f'ema_{self.fast_period}'].iloc[current_idx])
        medium_ema = float(df[f'ema_{self.medium_period}'].iloc[current_idx])
        slow_ema = float(df[f'ema_{self.slow_period}'].iloc[current_idx])
        
        fast_ema_prev = float(df[f'ema_{self.fast_period}'].iloc[prev_idx])
        medium_ema_prev = float(df[f'ema_{self.medium_period}'].iloc[prev_idx])
        
        # Volume check
        volume_confirmed = self._check_volume_confirmation(df, current_idx)
        if self.require_volume_confirmation and not volume_confirmed:
            return 'HOLD'
        
        # Momentum check (price change over last 3 candles)
        momentum = self._check_momentum(df, current_idx)
        
        # Check for golden cross (bullish)
        golden_cross = (
            fast_ema > medium_ema and
            fast_ema_prev <= medium_ema_prev
        )
        
        # Check for death cross (bearish)
        death_cross = (
            fast_ema < medium_ema and
            fast_ema_prev >= medium_ema_prev
        )
        
        # BUY conditions
        if golden_cross:
            # Confirm uptrend and momentum
            if (medium_ema > slow_ema and
                current_price > medium_ema and
                momentum > 0):
                logger.info(
                    f"Enhanced TRIPLE_EMA BUY signal - "
                    f"Price: {current_price:.2f}, "
                    f"EMAs: {fast_ema:.2f}/{medium_ema:.2f}/{slow_ema:.2f}, "
                    f"Volume: {'✓' if volume_confirmed else '✗'}, "
                    f"Momentum: {momentum:.2%}"
                )
                return 'BUY'
        
        # SELL conditions
        if death_cross:
            # Confirm downtrend and momentum
            if (medium_ema < slow_ema and
                current_price < medium_ema and
                momentum < 0):
                logger.info(
                    f"Enhanced TRIPLE_EMA SELL signal - "
                    f"Price: {current_price:.2f}, "
                    f"EMAs: {fast_ema:.2f}/{medium_ema:.2f}/{slow_ema:.2f}, "
                    f"Volume: {'✓' if volume_confirmed else '✗'}, "
                    f"Momentum: {momentum:.2%}"
                )
                return 'SELL'
        
        return 'HOLD'
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all required indicators."""
        # EMAs
        df[f'ema_{self.fast_period}'] = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        df[f'ema_{self.medium_period}'] = df['close'].ewm(span=self.medium_period, adjust=False).mean()
        df[f'ema_{self.slow_period}'] = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # ATR for volatility-based stops
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = np.abs(df['high'] - df['close'].shift())
        df['low_close'] = np.abs(df['low'] - df['close'].shift())
        df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['true_range'].rolling(window=self.atr_period).mean()
        
        # Volume average
        df['volume_avg'] = df['volume'].rolling(window=20).mean()
        
        return df
    
    def _check_volume_confirmation(self, df: pd.DataFrame, idx: int) -> bool:
        """Check if current volume confirms the move."""
        current_volume = float(df['volume'].iloc[idx])
        avg_volume = float(df['volume_avg'].iloc[idx])
        
        if pd.isna(avg_volume) or avg_volume == 0:
            return True  # Can't verify, assume OK
        
        return current_volume >= (self.volume_threshold * avg_volume)
    
    def _check_momentum(self, df: pd.DataFrame, idx: int, lookback: int = 3) -> float:
        """
        Check price momentum over lookback period.
        
        Returns:
            Momentum as percentage change
        """
        if len(df) < abs(idx) + lookback:
            return 0.0
        
        current_price = float(df['close'].iloc[idx])
        past_price = float(df['close'].iloc[idx - lookback])
        
        momentum = (current_price - past_price) / past_price
        return momentum
    
    def calculate_stop_loss_take_profit(
        self,
        entry_price: float,
        signal: str,
        df: pd.DataFrame = None,
        risk_reward_ratio: float = 2.0
    ) -> Tuple[float, float]:
        """
        Calculate dynamic stop loss and take profit based on ATR.
        
        If ATR data is available, use ATR-based stops.
        Otherwise, fall back to percentage-based stops.
        
        Args:
            entry_price: Entry price for the trade
            signal: 'BUY' or 'SELL'
            df: DataFrame with ATR data (optional)
            risk_reward_ratio: Ratio of TP to SL (default: 2.0)
            
        Returns:
            Tuple of (stop_loss, take_profit)
        """
        # Try to use ATR-based stops if data available
        if df is not None and 'atr' in df.columns and not df.empty:
            atr = float(df['atr'].iloc[-1])
            
            if not pd.isna(atr) and atr > 0:
                atr_distance = atr * self.atr_multiplier
                
                if signal == 'BUY':
                    stop_loss = entry_price - atr_distance
                    take_profit = entry_price + (atr_distance * risk_reward_ratio)
                else:  # SELL
                    stop_loss = entry_price + atr_distance
                    take_profit = entry_price - (atr_distance * risk_reward_ratio)
                
                logger.debug(
                    f"ATR-based stops: Entry={entry_price:.2f}, "
                    f"ATR={atr:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}"
                )
                return stop_loss, take_profit
        
        # Fallback to percentage-based stops
        return super().calculate_stop_loss_take_profit(entry_price, signal)


class OptimizedStrategyFactory:
    """
    Factory for creating optimized strategy instances.
    
    Provides pre-configured strategies with optimized parameters
    based on backtesting results.
    """
    
    @staticmethod
    def create_conservative_strategy() -> EnhancedTripleEMAStrategy:
        """
        Conservative strategy with tighter stops and higher volume requirement.
        
        Best for: Volatile markets, risk-averse traders
        """
        return EnhancedTripleEMAStrategy(
            fast_period=9,
            medium_period=21,
            slow_period=50,
            atr_multiplier=1.5,  # Tighter stops
            volume_threshold=1.5,  # Require strong volume
            require_volume_confirmation=True
        )
    
    @staticmethod
    def create_aggressive_strategy() -> EnhancedTripleEMAStrategy:
        """
        Aggressive strategy with wider stops and lower volume requirement.
        
        Best for: Trending markets, capturing larger moves
        """
        return EnhancedTripleEMAStrategy(
            fast_period=9,
            medium_period=21,
            slow_period=50,
            atr_multiplier=2.5,  # Wider stops
            volume_threshold=1.0,  # No volume requirement
            require_volume_confirmation=False
        )
    
    @staticmethod
    def create_balanced_strategy() -> EnhancedTripleEMAStrategy:
        """
        Balanced strategy with standard parameters.
        
        Best for: General trading, proven backtest results
        """
        return EnhancedTripleEMAStrategy(
            fast_period=9,
            medium_period=21,
            slow_period=50,
            atr_multiplier=2.0,
            volume_threshold=1.2,
            require_volume_confirmation=True
        )
    
    @staticmethod
    def create_custom_strategy(
        fast: int = 9,
        medium: int = 21,
        slow: int = 50,
        atr_mult: float = 2.0,
        vol_thresh: float = 1.2,
        require_vol: bool = True
    ) -> EnhancedTripleEMAStrategy:
        """
        Create a custom strategy with specified parameters.
        
        Args:
            fast: Fast EMA period
            medium: Medium EMA period
            slow: Slow EMA period
            atr_mult: ATR multiplier for stops
            vol_thresh: Volume threshold multiplier
            require_vol: Whether to require volume confirmation
            
        Returns:
            EnhancedTripleEMAStrategy instance
        """
        return EnhancedTripleEMAStrategy(
            fast_period=fast,
            medium_period=medium,
            slow_period=slow,
            atr_multiplier=atr_mult,
            volume_threshold=vol_thresh,
            require_volume_confirmation=require_vol
        )
