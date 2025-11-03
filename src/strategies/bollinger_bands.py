"""
Bollinger Bands Strategy
Volatility-based bands for breakout and reversal trading
"""
import pandas as pd
import numpy as np
from typing import Dict
from logger import get_logger

log = get_logger('BollingerBands')


class BollingerBandsStrategy:
    """
    Bollinger Bands Breakout/Reversal Strategy
    
    Bands = SMA ± (StdDev * multiplier)
    
    Signals:
    - BUY when price touches lower band with reversal
    - SELL when price touches upper band with reversal
    - Squeeze detection for high-probability breakouts
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0, squeeze_threshold: float = 0.02):
        self.period = period
        self.std_dev = std_dev
        self.squeeze_threshold = squeeze_threshold
        
    def calculate(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        close = df['close']
        sma = close.rolling(window=self.period).mean()
        std = close.rolling(window=self.period).std()
        
        upper = sma + (std * self.std_dev)
        lower = sma - (std * self.std_dev)
        
        # Band width (for squeeze detection)
        width = (upper - lower) / sma
        
        return {
            'upper': upper,
            'middle': sma,
            'lower': lower,
            'width': width,
            'std': std
        }
    
    def analyze(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Analyze price action relative to Bollinger Bands"""
        if len(df) < self.period + 5:
            return {
                'signal': 'HOLD',
                'strength': 'VERY_LOW',
                'reason': 'Insufficient data for Bollinger Bands'
            }
        
        bands = self.calculate(df)
        upper = bands['upper'].iloc[-1]
        middle = bands['middle'].iloc[-1]
        lower = bands['lower'].iloc[-1]
        width = bands['width'].iloc[-1]
        
        # Check for squeeze (low volatility)
        is_squeeze = width < self.squeeze_threshold
        
        # Price momentum
        recent_closes = df['close'].iloc[-3:]
        momentum_up = all(recent_closes.iloc[i] < recent_closes.iloc[i+1] for i in range(len(recent_closes)-1))
        momentum_down = all(recent_closes.iloc[i] > recent_closes.iloc[i+1] for i in range(len(recent_closes)-1))
        
        signal = 'HOLD'
        strength = 'VERY_LOW'
        reason = ''
        
        if is_squeeze:
            # Bands narrowing = wait for breakout
            reason = f'Bollinger squeeze detected (width {width*100:.2f}%)'
            strength = 'VERY_LOW'
        else:
            # Check band touches
            distance_to_lower = (current_price - lower) / current_price * 100
            distance_to_upper = (upper - current_price) / current_price * 100
            
            if distance_to_lower < 0.1:  # At lower band
                if momentum_up:
                    signal = 'BUY'
                    strength = 'HIGH'
                    reason = f'Bouncing off lower Bollinger Band (${lower:,.2f})'
                else:
                    strength = 'MODERATE'
                    reason = f'At lower band, waiting for reversal'
            
            elif distance_to_upper < 0.1:  # At upper band
                if momentum_down:
                    signal = 'SELL'
                    strength = 'HIGH'
                    reason = f'Rejecting upper Bollinger Band (${upper:,.2f})'
                else:
                    strength = 'MODERATE'
                    reason = f'At upper band, waiting for reversal'
            
            elif current_price < lower:  # Below lower band (oversold)
                signal = 'BUY'
                strength = 'MODERATE'
                reason = f'Price extended below lower band (${lower:,.2f})'
            
            elif current_price > upper:  # Above upper band (overbought)
                signal = 'SELL'
                strength = 'MODERATE'
                reason = f'Price extended above upper band (${upper:,.2f})'
        
        if signal != 'HOLD':
            log.info(f"📊 Bollinger Bands Analysis:")
            log.info(f"   Upper: ${upper:,.2f}")
            log.info(f"   Middle: ${middle:,.2f}")
            log.info(f"   Lower: ${lower:,.2f}")
            log.info(f"   Price: ${current_price:,.2f}")
            log.info(f"   Width: {width*100:.2f}%")
            log.info(f"   Signal: {signal} ({strength})")
        
        return {
            'signal': signal,
            'strength': strength,
            'reason': reason,
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'width': width,
            'is_squeeze': is_squeeze
        }


if __name__ == "__main__":
    # Test
    df = pd.DataFrame({
        'close': [50000 + i*100 + np.random.randint(-200, 200) for i in range(50)],
        'high': [50000 + i*100 + np.random.randint(0, 300) for i in range(50)],
        'low': [50000 + i*100 + np.random.randint(-300, 0) for i in range(50)]
    })
    
    strategy = BollingerBandsStrategy()
    result = strategy.analyze(df, df['close'].iloc[-1])
    print(f"\n📊 Bollinger Bands Test:")
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Is Squeeze: {result['is_squeeze']}")
