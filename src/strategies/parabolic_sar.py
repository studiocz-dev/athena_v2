"""
Parabolic SAR Strategy
Trend following with clear reversal signals
"""
import pandas as pd
import numpy as np
from typing import Dict
from logger import get_logger

log = get_logger('ParabolicSAR')


class ParabolicSARStrategy:
    """
    Parabolic SAR (Stop and Reverse) Strategy
    
    SAR dots above price = downtrend (sell signal)
    SAR dots below price = uptrend (buy signal)
    
    Crosses indicate trend reversals
    """
    
    def __init__(self, acceleration: float = 0.02, maximum: float = 0.2):
        self.acceleration = acceleration  # AF increment
        self.maximum = maximum  # Max AF
        
    def calculate_sar(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate Parabolic SAR
        
        Manual implementation since we might not have talib
        """
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        sar = np.zeros(len(df))
        ep = np.zeros(len(df))  # Extreme point
        af = np.zeros(len(df))  # Acceleration factor
        trend = np.zeros(len(df))  # 1 = uptrend, -1 = downtrend
        
        # Initialize
        sar[0] = low[0]
        ep[0] = high[0]
        af[0] = self.acceleration
        trend[0] = 1  # Start with uptrend
        
        for i in range(1, len(df)):
            # Previous values
            prev_sar = sar[i-1]
            prev_ep = ep[i-1]
            prev_af = af[i-1]
            prev_trend = trend[i-1]
            
            # Calculate new SAR
            sar[i] = prev_sar + prev_af * (prev_ep - prev_sar)
            
            # Uptrend
            if prev_trend == 1:
                # Check for reversal
                if low[i] < sar[i]:
                    # Reversal to downtrend
                    trend[i] = -1
                    sar[i] = prev_ep  # SAR becomes the EP
                    ep[i] = low[i]
                    af[i] = self.acceleration
                else:
                    # Continue uptrend
                    trend[i] = 1
                    
                    # Update EP if new high
                    if high[i] > prev_ep:
                        ep[i] = high[i]
                        af[i] = min(prev_af + self.acceleration, self.maximum)
                    else:
                        ep[i] = prev_ep
                        af[i] = prev_af
                    
                    # SAR should not be above prior two lows
                    sar[i] = min(sar[i], low[i-1])
                    if i > 1:
                        sar[i] = min(sar[i], low[i-2])
            
            # Downtrend
            else:
                # Check for reversal
                if high[i] > sar[i]:
                    # Reversal to uptrend
                    trend[i] = 1
                    sar[i] = prev_ep  # SAR becomes the EP
                    ep[i] = high[i]
                    af[i] = self.acceleration
                else:
                    # Continue downtrend
                    trend[i] = -1
                    
                    # Update EP if new low
                    if low[i] < prev_ep:
                        ep[i] = low[i]
                        af[i] = min(prev_af + self.acceleration, self.maximum)
                    else:
                        ep[i] = prev_ep
                        af[i] = prev_af
                    
                    # SAR should not be below prior two highs
                    sar[i] = max(sar[i], high[i-1])
                    if i > 1:
                        sar[i] = max(sar[i], high[i-2])
        
        return pd.Series(sar, index=df.index), pd.Series(trend, index=df.index)
    
    def analyze(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Analyze trend using Parabolic SAR
        
        Args:
            df: OHLCV DataFrame
            current_price: Current market price
            
        Returns:
            Signal dictionary
        """
        if len(df) < 20:
            return {
                'signal': 'HOLD',
                'strength': 'VERY_LOW',
                'reason': 'Insufficient data for Parabolic SAR'
            }
        
        sar, trend = self.calculate_sar(df)
        
        # Current values
        sar_curr = sar.iloc[-1]
        sar_prev = sar.iloc[-2]
        trend_curr = trend.iloc[-1]
        trend_prev = trend.iloc[-2]
        
        close_prev = df['close'].iloc[-2]
        
        signal = 'HOLD'
        strength = 'VERY_LOW'
        reason = ''
        
        # Check for reversal
        if trend_curr == 1 and trend_prev == -1:
            # Just flipped to uptrend
            signal = 'BUY'
            strength = 'HIGH'
            reason = f'Parabolic SAR reversal to uptrend (SAR: ${sar_curr:,.2f})'
        
        elif trend_curr == -1 and trend_prev == 1:
            # Just flipped to downtrend
            signal = 'SELL'
            strength = 'HIGH'
            reason = f'Parabolic SAR reversal to downtrend (SAR: ${sar_curr:,.2f})'
        
        # Continuation signals
        elif trend_curr == 1:
            # In uptrend
            if current_price > sar_curr:
                signal = 'BUY'
                strength = 'MODERATE'
                reason = f'Parabolic SAR uptrend continuation (SAR: ${sar_curr:,.2f})'
            else:
                strength = 'LOW'
                reason = f'Uptrend weakening, price near SAR'
        
        elif trend_curr == -1:
            # In downtrend
            if current_price < sar_curr:
                signal = 'SELL'
                strength = 'MODERATE'
                reason = f'Parabolic SAR downtrend continuation (SAR: ${sar_curr:,.2f})'
            else:
                strength = 'LOW'
                reason = f'Downtrend weakening, price near SAR'
        
        # Calculate distance from SAR (risk/stop level)
        distance_percent = abs(current_price - sar_curr) / current_price * 100
        
        if signal != 'HOLD':
            log.info(f"🎯 Parabolic SAR Analysis:")
            log.info(f"   Price: ${current_price:,.2f}")
            log.info(f"   SAR: ${sar_curr:,.2f}")
            log.info(f"   Trend: {'Uptrend' if trend_curr == 1 else 'Downtrend'}")
            log.info(f"   Distance from SAR: {distance_percent:.2f}%")
            log.info(f"   Signal: {signal} ({strength})")
        
        return {
            'signal': signal,
            'strength': strength,
            'reason': reason,
            'sar': sar_curr,
            'trend': 'UP' if trend_curr == 1 else 'DOWN',
            'distance_percent': distance_percent,
            'reversal': trend_curr != trend_prev
        }


if __name__ == "__main__":
    # Test with trending data
    base_price = 50000
    
    # Create uptrend then downtrend
    uptrend = [base_price + i*100 for i in range(30)]
    downtrend = [uptrend[-1] - i*80 for i in range(30)]
    
    df = pd.DataFrame({
        'close': uptrend + downtrend,
        'high': [p + np.random.randint(0, 200) for p in uptrend + downtrend],
        'low': [p + np.random.randint(-200, 0) for p in uptrend + downtrend],
    })
    
    strategy = ParabolicSARStrategy()
    
    # Test at different points
    print("\n🎯 Parabolic SAR Test:")
    
    # During uptrend
    result = strategy.analyze(df.iloc[:30], df.iloc[29]['close'])
    print(f"\n   During Uptrend:")
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Trend: {result['trend']}")
    
    # At reversal
    result = strategy.analyze(df.iloc[:35], df.iloc[34]['close'])
    print(f"\n   At Reversal Point:")
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reversal: {result['reversal']}")
    
    # During downtrend
    result = strategy.analyze(df, df.iloc[-1]['close'])
    print(f"\n   During Downtrend:")
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Trend: {result['trend']}")
