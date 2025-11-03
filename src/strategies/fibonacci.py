"""
Fibonacci Retracement Strategy
Golden ratio entries on pullbacks
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from logger import get_logger

log = get_logger('Fibonacci')


class FibonacciStrategy:
    """
    Fibonacci Retracement Strategy
    
    Identifies swing highs/lows and calculates Fibonacci levels
    Entries at key retracement levels (0.382, 0.5, 0.618, 0.786)
    
    Golden ratio (0.618) is the strongest level
    """
    
    def __init__(self, lookback: int = 50):
        self.lookback = lookback
        self.fib_levels = {
            '0.0': 0.0,
            '0.236': 0.236,
            '0.382': 0.382,
            '0.5': 0.5,
            '0.618': 0.618,  # Golden ratio - strongest
            '0.786': 0.786,
            '1.0': 1.0
        }
        
    def find_swing_points(self, df: pd.DataFrame) -> Tuple[float, float, int, int]:
        """
        Find recent swing high and swing low
        
        Returns:
            (swing_high, swing_low, high_index, low_index)
        """
        lookback_df = df.iloc[-self.lookback:]
        
        swing_high = lookback_df['high'].max()
        swing_low = lookback_df['low'].min()
        
        high_idx = lookback_df['high'].idxmax()
        low_idx = lookback_df['low'].idxmin()
        
        return swing_high, swing_low, high_idx, low_idx
    
    def calculate_fib_levels(self, swing_high: float, swing_low: float, 
                            trend: str = 'UP') -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels
        
        Args:
            swing_high: Swing high price
            swing_low: Swing low price
            trend: 'UP' for uptrend (retrace from high), 'DOWN' for downtrend
            
        Returns:
            Dictionary with Fibonacci levels
        """
        diff = swing_high - swing_low
        
        if trend == 'UP':
            # Retracing from high to low (looking for long entries)
            levels = {
                name: swing_high - (diff * ratio)
                for name, ratio in self.fib_levels.items()
            }
        else:
            # Retracing from low to high (looking for short entries)
            levels = {
                name: swing_low + (diff * ratio)
                for name, ratio in self.fib_levels.items()
            }
        
        return levels
    
    def find_nearest_fib_level(self, price: float, fib_levels: Dict[str, float]) -> Tuple[str, float, float]:
        """Find nearest Fibonacci level"""
        min_distance = float('inf')
        nearest_level = None
        nearest_price = 0
        
        for level_name, level_price in fib_levels.items():
            distance = abs(price - level_price) / price * 100
            if distance < min_distance:
                min_distance = distance
                nearest_level = level_name
                nearest_price = level_price
        
        return nearest_level, nearest_price, min_distance
    
    def determine_trend(self, df: pd.DataFrame) -> str:
        """Determine if we're in uptrend or downtrend"""
        swing_high, swing_low, high_idx, low_idx = self.find_swing_points(df)
        
        # If swing high is more recent than swing low = uptrend
        if high_idx > low_idx:
            return 'UP'
        else:
            return 'DOWN'
    
    def analyze(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Analyze price relative to Fibonacci levels
        
        Args:
            df: OHLCV DataFrame
            current_price: Current market price
            
        Returns:
            Signal dictionary
        """
        if len(df) < self.lookback:
            return {
                'signal': 'HOLD',
                'strength': 'VERY_LOW',
                'reason': 'Insufficient data for Fibonacci'
            }
        
        # Find swing points
        swing_high, swing_low, high_idx, low_idx = self.find_swing_points(df)
        
        # Determine trend
        trend = self.determine_trend(df)
        
        # Calculate Fib levels
        fib_levels = self.calculate_fib_levels(swing_high, swing_low, trend)
        
        # Find nearest level
        nearest_level, nearest_price, distance = self.find_nearest_fib_level(current_price, fib_levels)
        
        # Proximity threshold (0.3% = near level)
        proximity_threshold = 0.3
        
        signal = 'HOLD'
        strength = 'VERY_LOW'
        reason = ''
        
        if distance < proximity_threshold:
            # Price near a Fibonacci level
            if trend == 'UP':
                # Uptrend - looking for long entries on retracement
                if nearest_level == '0.618':
                    # Golden ratio - strongest level
                    signal = 'BUY'
                    strength = 'HIGH'
                    reason = f'Golden ratio (0.618) support at ${nearest_price:,.2f}'
                
                elif nearest_level in ['0.5', '0.382']:
                    # Other strong levels
                    signal = 'BUY'
                    strength = 'MODERATE'
                    reason = f'Fib {nearest_level} support at ${nearest_price:,.2f}'
                
                elif nearest_level == '0.786':
                    # Deep retracement
                    signal = 'BUY'
                    strength = 'LOW'
                    reason = f'Deep retracement (0.786) at ${nearest_price:,.2f}'
            
            else:  # Downtrend
                # Downtrend - looking for short entries on bounce
                if nearest_level == '0.618':
                    signal = 'SELL'
                    strength = 'HIGH'
                    reason = f'Golden ratio (0.618) resistance at ${nearest_price:,.2f}'
                
                elif nearest_level in ['0.5', '0.382']:
                    signal = 'SELL'
                    strength = 'MODERATE'
                    reason = f'Fib {nearest_level} resistance at ${nearest_price:,.2f}'
                
                elif nearest_level == '0.786':
                    signal = 'SELL'
                    strength = 'LOW'
                    reason = f'Deep bounce (0.786) at ${nearest_price:,.2f}'
        
        else:
            # Price between levels
            strength = 'VERY_LOW'
            reason = f'Price between Fib levels (nearest: {nearest_level} at {distance:.2f}%)'
        
        if signal != 'HOLD' or distance < 1.0:
            log.info(f"📐 Fibonacci Analysis:")
            log.info(f"   Trend: {trend}trend")
            log.info(f"   Swing High: ${swing_high:,.2f}")
            log.info(f"   Swing Low: ${swing_low:,.2f}")
            log.info(f"   Current: ${current_price:,.2f}")
            log.info(f"   Nearest Level: {nearest_level} @ ${nearest_price:,.2f} ({distance:.2f}% away)")
            if signal != 'HOLD':
                log.info(f"   Signal: {signal} ({strength})")
        
        return {
            'signal': signal,
            'strength': strength,
            'reason': reason,
            'swing_high': swing_high,
            'swing_low': swing_low,
            'trend': trend,
            'fib_levels': fib_levels,
            'nearest_level': nearest_level,
            'nearest_price': nearest_price,
            'distance_percent': distance
        }
    
    def get_fib_levels_text(self, fib_levels: Dict[str, float], current_price: float) -> str:
        """Format Fib levels as text"""
        text = "📐 Fibonacci Levels:\n"
        
        sorted_levels = sorted(fib_levels.items(), key=lambda x: x[1], reverse=True)
        
        for name, price in sorted_levels:
            marker = " 🎯" if abs(current_price - price) / current_price < 0.003 else ""
            golden = " ⭐" if name == '0.618' else ""
            text += f"{name}: ${price:,.2f}{marker}{golden}\n"
        
        return text


if __name__ == "__main__":
    # Test
    base_price = 50000
    trend_data = [base_price + i*100 for i in range(30)]  # Uptrend
    trend_data += [trend_data[-1] - i*50 for i in range(20)]  # Retracement
    
    df = pd.DataFrame({
        'close': trend_data + [np.random.randint(-100, 100) for _ in range(10)],
        'high': [p + np.random.randint(0, 200) for p in trend_data + [trend_data[-1]]*10],
        'low': [p + np.random.randint(-200, 0) for p in trend_data + [trend_data[-1]]*10],
    })
    
    strategy = FibonacciStrategy(lookback=50)
    result = strategy.analyze(df, df['close'].iloc[-1])
    
    print(f"\n📐 Fibonacci Test:")
    print(f"   Trend: {result['trend']}")
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reason: {result['reason']}")
    print(f"\n{strategy.get_fib_levels_text(result['fib_levels'], df['close'].iloc[-1])}")
