"""
VWAP (Volume-Weighted Average Price) Strategy
Institutional traders use VWAP as a benchmark for intraday trading
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from logger import get_logger

log = get_logger('VWAP')


class VWAPStrategy:
    """
    VWAP Bounce Strategy
    
    VWAP = Sum(Price * Volume) / Sum(Volume)
    
    Concept:
    - VWAP acts as dynamic support/resistance for the day
    - Price above VWAP = bullish, institutions buying
    - Price below VWAP = bearish, institutions selling
    - Bounces off VWAP = high-probability entries
    
    Signals:
    - BUY when price bounces off VWAP from below
    - SELL when price rejects VWAP from above
    - Strength based on distance and momentum
    """
    
    def __init__(self, distance_threshold: float = 0.002):
        """
        Initialize VWAP strategy
        
        Args:
            distance_threshold: Max distance from VWAP to trigger signal (0.2% default)
        """
        self.distance_threshold = distance_threshold
        
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate VWAP for the session
        
        Args:
            df: DataFrame with OHLCV data (intraday)
            
        Returns:
            Series with VWAP values
        """
        # Typical price = (High + Low + Close) / 3
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        
        # Price * Volume
        df['tp_volume'] = df['typical_price'] * df['volume']
        
        # Cumulative sums
        df['cumulative_tp_volume'] = df['tp_volume'].cumsum()
        df['cumulative_volume'] = df['volume'].cumsum()
        
        # VWAP = Cumulative(Price*Volume) / Cumulative(Volume)
        df['vwap'] = df['cumulative_tp_volume'] / df['cumulative_volume']
        
        return df['vwap']
    
    def calculate_vwap_bands(self, df: pd.DataFrame, std_mult: float = 1.0) -> Dict[str, pd.Series]:
        """
        Calculate VWAP with standard deviation bands
        
        Args:
            df: DataFrame with OHLCV data
            std_mult: Standard deviation multiplier
            
        Returns:
            Dictionary with vwap, upper_band, lower_band
        """
        vwap = self.calculate_vwap(df)
        
        # Calculate standard deviation of typical price from VWAP
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        df['squared_diff'] = (df['typical_price'] - vwap) ** 2
        df['cumsum_squared_diff'] = df['squared_diff'].cumsum()
        df['cumsum_volume'] = df['volume'].cumsum()
        
        # Weighted standard deviation
        variance = df['cumsum_squared_diff'] / df['cumsum_volume']
        std_dev = np.sqrt(variance)
        
        upper_band = vwap + (std_dev * std_mult)
        lower_band = vwap - (std_dev * std_mult)
        
        return {
            'vwap': vwap,
            'upper_band': upper_band,
            'lower_band': lower_band,
            'std_dev': std_dev
        }
    
    def analyze(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Analyze price action relative to VWAP
        
        Args:
            df: DataFrame with intraday OHLCV data
            current_price: Current market price
            
        Returns:
            Signal dictionary
        """
        if len(df) < 10:
            return {
                'signal': 'HOLD',
                'strength': 'VERY_LOW',
                'reason': 'Insufficient data for VWAP',
                'vwap': 0,
                'distance_percent': 0
            }
        
        # Calculate VWAP and bands
        vwap_data = self.calculate_vwap_bands(df)
        vwap = vwap_data['vwap'].iloc[-1]
        upper_band = vwap_data['upper_band'].iloc[-1]
        lower_band = vwap_data['lower_band'].iloc[-1]
        
        # Calculate distance from VWAP
        distance = (current_price - vwap) / vwap
        distance_percent = abs(distance) * 100
        
        # Price momentum (last 3 candles)
        recent_closes = df['close'].iloc[-3:]
        momentum_up = all(recent_closes.iloc[i] < recent_closes.iloc[i+1] for i in range(len(recent_closes)-1))
        momentum_down = all(recent_closes.iloc[i] > recent_closes.iloc[i+1] for i in range(len(recent_closes)-1))
        
        signal = 'HOLD'
        strength = 'VERY_LOW'
        reason = ''
        
        # Check if near VWAP
        if distance_percent < self.distance_threshold * 100:
            # Very close to VWAP
            if current_price < vwap:
                # Below VWAP, looking for bounce
                if momentum_up:
                    signal = 'BUY'
                    strength = 'MODERATE'
                    reason = f'Bouncing off VWAP from below (${vwap:,.2f})'
                else:
                    strength = 'LOW'
                    reason = f'At VWAP support but no momentum'
            
            elif current_price > vwap:
                # Above VWAP, looking for rejection
                if momentum_down:
                    signal = 'SELL'
                    strength = 'MODERATE'
                    reason = f'Rejecting VWAP from above (${vwap:,.2f})'
                else:
                    strength = 'LOW'
                    reason = f'At VWAP resistance but no rejection'
            
            else:
                # Exactly at VWAP
                strength = 'VERY_LOW'
                reason = 'Price at VWAP (neutral zone)'
        
        # Check if at VWAP bands
        elif current_price <= lower_band:
            # At lower band = oversold
            if momentum_up:
                signal = 'BUY'
                strength = 'HIGH'
                reason = f'Bouncing off lower VWAP band (${lower_band:,.2f})'
            else:
                strength = 'MODERATE'
                reason = f'At lower VWAP band, waiting for bounce'
        
        elif current_price >= upper_band:
            # At upper band = overbought
            if momentum_down:
                signal = 'SELL'
                strength = 'HIGH'
                reason = f'Rejecting upper VWAP band (${upper_band:,.2f})'
            else:
                strength = 'MODERATE'
                reason = f'At upper VWAP band, waiting for rejection'
        
        else:
            # Price away from VWAP
            if current_price > vwap:
                strength = 'VERY_LOW'
                reason = f'Price {distance_percent:.2f}% above VWAP (bullish zone)'
            else:
                strength = 'VERY_LOW'
                reason = f'Price {distance_percent:.2f}% below VWAP (bearish zone)'
        
        # Log significant signals
        if signal != 'HOLD' or distance_percent < 0.5:
            log.info(f"📊 VWAP Analysis:")
            log.info(f"   Price: ${current_price:,.2f}")
            log.info(f"   VWAP: ${vwap:,.2f} ({'+' if distance > 0 else ''}{distance_percent:.2f}%)")
            log.info(f"   Bands: ${lower_band:,.2f} - ${upper_band:,.2f}")
            log.info(f"   Signal: {signal} ({strength})")
        
        return {
            'signal': signal,
            'strength': strength,
            'reason': reason,
            'vwap': vwap,
            'upper_band': upper_band,
            'lower_band': lower_band,
            'distance_percent': distance_percent,
            'position_relative': 'ABOVE' if current_price > vwap else 'BELOW' if current_price < vwap else 'AT'
        }
    
    def get_vwap_text(self, vwap: float, upper: float, lower: float, current: float) -> str:
        """
        Format VWAP levels as text
        
        Args:
            vwap: VWAP value
            upper: Upper band
            lower: Lower band
            current: Current price
            
        Returns:
            Formatted string
        """
        distance = (current - vwap) / vwap * 100
        position = "🟢 ABOVE" if current > vwap else "🔴 BELOW" if current < vwap else "🟡 AT"
        
        text = f"📊 VWAP Levels:\n"
        text += f"Upper Band: ${upper:,.2f}\n"
        text += f"VWAP: ${vwap:,.2f}\n"
        text += f"Lower Band: ${lower:,.2f}\n"
        text += f"Current: ${current:,.2f} {position} ({distance:+.2f}%)"
        
        return text


# Example usage
if __name__ == "__main__":
    # Test with sample intraday data
    np.random.seed(42)
    
    # Generate 50 15-minute candles (one trading session)
    base_price = 50000
    df = pd.DataFrame({
        'timestamp': pd.date_range('2025-01-01 00:00', periods=50, freq='15min'),
        'high': [base_price + np.random.randint(-200, 300) for _ in range(50)],
        'low': [base_price + np.random.randint(-300, 200) for _ in range(50)],
        'close': [base_price + np.random.randint(-250, 250) for _ in range(50)],
        'volume': [np.random.randint(100, 1000) for _ in range(50)]
    })
    df['open'] = df['close'].shift(1).fillna(base_price)
    
    strategy = VWAPStrategy()
    
    # Calculate VWAP
    vwap_data = strategy.calculate_vwap_bands(df)
    vwap = vwap_data['vwap'].iloc[-1]
    upper = vwap_data['upper_band'].iloc[-1]
    lower = vwap_data['lower_band'].iloc[-1]
    
    print("\n" + strategy.get_vwap_text(vwap, upper, lower, df['close'].iloc[-1]))
    
    # Test signals at different price levels
    print("\n📊 Test 1: Price at VWAP")
    result = strategy.analyze(df, vwap * 1.001)
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reason: {result['reason']}")
    
    print("\n📊 Test 2: Price at lower band")
    result = strategy.analyze(df, lower * 0.999)
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reason: {result['reason']}")
    
    print("\n📊 Test 3: Price at upper band")
    result = strategy.analyze(df, upper * 1.001)
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reason: {result['reason']}")
