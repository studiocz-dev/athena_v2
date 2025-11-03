"""
Pivot Points Strategy
Calculates daily pivot points and generates signals based on support/resistance bounces
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from logger import get_logger

log = get_logger('PivotPoints')


class PivotPointsStrategy:
    """
    Pivot Points Support/Resistance Strategy
    
    Classic pivot point formula:
    - Pivot = (High + Low + Close) / 3
    - R1 = 2*Pivot - Low
    - R2 = Pivot + (High - Low)
    - R3 = High + 2*(Pivot - Low)
    - S1 = 2*Pivot - High
    - S2 = Pivot - (High - Low)
    - S3 = Low - 2*(High - Pivot)
    
    Signals:
    - BUY when price bounces off S1/S2 with oversold RSI
    - SELL when price rejects R1/R2 with overbought RSI
    """
    
    def __init__(self, rsi_threshold: float = 35):
        """
        Initialize Pivot Points strategy
        
        Args:
            rsi_threshold: RSI threshold for oversold (default 35)
        """
        self.rsi_threshold = rsi_threshold
        self.pivots = {}
        
    def calculate_pivot_points(self, high: float, low: float, close: float) -> Dict[str, float]:
        """
        Calculate pivot points from previous day's data
        
        Args:
            high: Previous day's high
            low: Previous day's low
            close: Previous day's close
            
        Returns:
            Dictionary with pivot and support/resistance levels
        """
        pivot = (high + low + close) / 3
        
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            'r3': r3,
            's1': s1,
            's2': s2,
            's3': s3
        }
    
    def calculate_pivots_from_df(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate pivot points from daily timeframe DataFrame
        
        Args:
            df: DataFrame with OHLCV data (daily timeframe)
            
        Returns:
            Pivot point levels
        """
        if len(df) < 2:
            return {}
        
        # Use previous day's data
        prev_day = df.iloc[-2]
        high = prev_day['high']
        low = prev_day['low']
        close = prev_day['close']
        
        return self.calculate_pivot_points(high, low, close)
    
    def find_nearest_level(self, price: float, pivots: Dict[str, float]) -> Tuple[str, float, float]:
        """
        Find the nearest pivot level
        
        Args:
            price: Current price
            pivots: Pivot point levels
            
        Returns:
            (level_name, level_price, distance_percent)
        """
        if not pivots:
            return None, 0, 100
        
        min_distance = float('inf')
        nearest_level = None
        nearest_price = 0
        
        for level_name, level_price in pivots.items():
            distance = abs(price - level_price) / price * 100
            if distance < min_distance:
                min_distance = distance
                nearest_level = level_name
                nearest_price = level_price
        
        return nearest_level, nearest_price, min_distance
    
    def analyze(self, df: pd.DataFrame, current_price: float, rsi: float) -> Dict:
        """
        Analyze price action relative to pivot points
        
        Args:
            df: DataFrame with daily OHLCV data
            current_price: Current market price
            rsi: Current RSI value
            
        Returns:
            Signal dictionary with action, strength, and details
        """
        # Calculate pivot points
        pivots = self.calculate_pivots_from_df(df)
        
        if not pivots:
            return {
                'signal': 'HOLD',
                'strength': 'VERY_LOW',
                'reason': 'Insufficient data for pivot calculation',
                'pivots': {}
            }
        
        # Find nearest level
        nearest_level, nearest_price, distance = self.find_nearest_level(current_price, pivots)
        
        # Proximity threshold (0.2% = within level zone)
        proximity_threshold = 0.2
        
        signal = 'HOLD'
        strength = 'VERY_LOW'
        reason = ''
        
        # Support levels (S1, S2, S3)
        if nearest_level in ['s1', 's2', 's3']:
            if distance < proximity_threshold:
                # At support level
                if rsi < self.rsi_threshold:
                    # Oversold at support = strong buy
                    signal = 'BUY'
                    strength = 'HIGH' if nearest_level == 's1' else 'MODERATE'
                    reason = f'Oversold (RSI {rsi:.1f}) at support {nearest_level.upper()}'
                elif rsi < 45:
                    # Neutral RSI at support = moderate buy
                    signal = 'BUY'
                    strength = 'MODERATE'
                    reason = f'Price bouncing at support {nearest_level.upper()}'
                else:
                    strength = 'LOW'
                    reason = f'At support {nearest_level.upper()} but RSI not oversold'
        
        # Resistance levels (R1, R2, R3)
        elif nearest_level in ['r1', 'r2', 'r3']:
            if distance < proximity_threshold:
                # At resistance level
                if rsi > (100 - self.rsi_threshold):
                    # Overbought at resistance = strong sell
                    signal = 'SELL'
                    strength = 'HIGH' if nearest_level == 'r1' else 'MODERATE'
                    reason = f'Overbought (RSI {rsi:.1f}) at resistance {nearest_level.upper()}'
                elif rsi > 55:
                    # Elevated RSI at resistance = moderate sell
                    signal = 'SELL'
                    strength = 'MODERATE'
                    reason = f'Price rejecting resistance {nearest_level.upper()}'
                else:
                    strength = 'LOW'
                    reason = f'At resistance {nearest_level.upper()} but RSI not overbought'
        
        # Pivot point itself
        elif nearest_level == 'pivot':
            if distance < proximity_threshold:
                # At pivot = neutral zone
                strength = 'VERY_LOW'
                reason = f'Price at pivot point (neutral zone)'
        
        # Log analysis
        if signal != 'HOLD' or distance < proximity_threshold:
            log.info(f"📍 Pivot Analysis:")
            log.info(f"   Price: ${current_price:,.2f}")
            log.info(f"   Nearest: {nearest_level.upper()} @ ${nearest_price:,.2f} ({distance:.2f}% away)")
            log.info(f"   RSI: {rsi:.1f}")
            log.info(f"   Signal: {signal} ({strength})")
        
        return {
            'signal': signal,
            'strength': strength,
            'reason': reason,
            'pivots': pivots,
            'nearest_level': nearest_level,
            'nearest_price': nearest_price,
            'distance_percent': distance,
            'rsi': rsi
        }
    
    def get_pivot_levels_text(self, pivots: Dict[str, float]) -> str:
        """
        Format pivot levels as text for logging/Discord
        
        Args:
            pivots: Pivot point levels
            
        Returns:
            Formatted string
        """
        if not pivots:
            return "No pivot data"
        
        text = "📊 Pivot Levels:\n"
        text += f"R3: ${pivots['r3']:,.2f}\n"
        text += f"R2: ${pivots['r2']:,.2f}\n"
        text += f"R1: ${pivots['r1']:,.2f}\n"
        text += f"PP: ${pivots['pivot']:,.2f}\n"
        text += f"S1: ${pivots['s1']:,.2f}\n"
        text += f"S2: ${pivots['s2']:,.2f}\n"
        text += f"S3: ${pivots['s3']:,.2f}"
        
        return text


def calculate_rsi(series: pd.Series, period: int = 14) -> float:
    """Calculate RSI from price series"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1] if len(rsi) > 0 else 50


# Example usage
if __name__ == "__main__":
    # Test with sample data
    dates = pd.date_range('2025-01-01', periods=10, freq='D')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': [50000, 50500, 50200, 49800, 49500, 50000, 50500, 51000, 50800, 50600],
        'high': [50800, 51000, 50600, 50200, 50000, 50600, 51200, 51500, 51200, 51000],
        'low': [49800, 50200, 49800, 49400, 49200, 49700, 50200, 50700, 50500, 50300],
        'close': [50500, 50400, 50000, 49600, 49800, 50400, 51000, 51200, 50900, 50700],
        'volume': [1000] * 10
    })
    
    strategy = PivotPointsStrategy()
    
    # Calculate pivots
    pivots = strategy.calculate_pivots_from_df(df)
    print("\n" + strategy.get_pivot_levels_text(pivots))
    
    # Test signals at different price levels
    current_price = pivots['s1'] * 1.001  # Just above S1
    rsi = 32  # Oversold
    
    result = strategy.analyze(df, current_price, rsi)
    print(f"\n📊 Test Analysis:")
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reason: {result['reason']}")
