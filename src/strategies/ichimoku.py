"""
Ichimoku Cloud Strategy
Comprehensive trend-following system
"""
import pandas as pd
import numpy as np
from typing import Dict
from logger import get_logger

log = get_logger('Ichimoku')


class IchimokuStrategy:
    """
    Ichimoku Cloud (Ichimoku Kinko Hyo) Strategy
    
    Components:
    - Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
    - Kijun-sen (Base Line): (26-period high + 26-period low) / 2
    - Senkou Span A: (Tenkan + Kijun) / 2, shifted 26 forward
    - Senkou Span B: (52-period high + 52-period low) / 2, shifted 26 forward
    - Chikou Span: Current close shifted 26 backward
    
    Cloud = space between Senkou A and B
    
    Signals:
    - Strong bullish: Price above cloud, Tenkan > Kijun, Chikou > price
    - Strong bearish: Price below cloud, Tenkan < Kijun, Chikou < price
    """
    
    def __init__(self):
        self.tenkan_period = 9
        self.kijun_period = 26
        self.senkou_b_period = 52
        self.displacement = 26
        
    def calculate_ichimoku(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate all Ichimoku components"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Tenkan-sen (Conversion Line)
        tenkan_high = high.rolling(window=self.tenkan_period).max()
        tenkan_low = low.rolling(window=self.tenkan_period).min()
        tenkan_sen = (tenkan_high + tenkan_low) / 2
        
        # Kijun-sen (Base Line)
        kijun_high = high.rolling(window=self.kijun_period).max()
        kijun_low = low.rolling(window=self.kijun_period).min()
        kijun_sen = (kijun_high + kijun_low) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(self.displacement)
        
        # Senkou Span B (Leading Span B)
        senkou_high = high.rolling(window=self.senkou_b_period).max()
        senkou_low = low.rolling(window=self.senkou_b_period).min()
        senkou_span_b = ((senkou_high + senkou_low) / 2).shift(self.displacement)
        
        # Chikou Span (Lagging Span)
        chikou_span = close.shift(-self.displacement)
        
        return {
            'tenkan': tenkan_sen,
            'kijun': kijun_sen,
            'senkou_a': senkou_span_a,
            'senkou_b': senkou_span_b,
            'chikou': chikou_span
        }
    
    def analyze(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Analyze trend using Ichimoku Cloud
        
        Args:
            df: OHLCV DataFrame
            current_price: Current market price
            
        Returns:
            Signal dictionary
        """
        min_length = self.senkou_b_period + self.displacement + 10
        if len(df) < min_length:
            return {
                'signal': 'HOLD',
                'strength': 'VERY_LOW',
                'reason': 'Insufficient data for Ichimoku'
            }
        
        ichimoku = self.calculate_ichimoku(df)
        
        # Current values (use -displacement for cloud since it's shifted forward)
        idx = -self.displacement if len(df) > self.displacement else -1
        
        tenkan = ichimoku['tenkan'].iloc[-1]
        kijun = ichimoku['kijun'].iloc[-1]
        senkou_a = ichimoku['senkou_a'].iloc[idx] if not pd.isna(ichimoku['senkou_a'].iloc[idx]) else ichimoku['senkou_a'].iloc[-1]
        senkou_b = ichimoku['senkou_b'].iloc[idx] if not pd.isna(ichimoku['senkou_b'].iloc[idx]) else ichimoku['senkou_b'].iloc[-1]
        
        # Chikou span comparison (price 26 periods ago)
        chikou_idx = -self.displacement - 1
        if abs(chikou_idx) < len(ichimoku['chikou']):
            chikou = df['close'].iloc[-1]  # Current close
            chikou_price = df['close'].iloc[chikou_idx]  # Price 26 periods ago
        else:
            chikou = 0
            chikou_price = 0
        
        # Cloud boundaries
        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)
        
        # Determine cloud color
        cloud_color = 'BULLISH' if senkou_a > senkou_b else 'BEARISH'
        
        # Check conditions
        conditions = {
            'price_above_cloud': current_price > cloud_top,
            'price_below_cloud': current_price < cloud_bottom,
            'price_in_cloud': cloud_bottom <= current_price <= cloud_top,
            'tenkan_above_kijun': tenkan > kijun,
            'tenkan_below_kijun': tenkan < kijun,
            'chikou_above_price': chikou > chikou_price if chikou_price > 0 else False,
            'chikou_below_price': chikou < chikou_price if chikou_price > 0 else False,
            'cloud_bullish': cloud_color == 'BULLISH',
            'cloud_bearish': cloud_color == 'BEARISH'
        }
        
        # Count bullish/bearish signals
        bullish_signals = []
        bearish_signals = []
        
        if conditions['price_above_cloud']:
            bullish_signals.append("Price above cloud")
        if conditions['price_below_cloud']:
            bearish_signals.append("Price below cloud")
        
        if conditions['tenkan_above_kijun']:
            bullish_signals.append("Tenkan > Kijun")
        if conditions['tenkan_below_kijun']:
            bearish_signals.append("Tenkan < Kijun")
        
        if conditions['chikou_above_price']:
            bullish_signals.append("Chikou above price")
        if conditions['chikou_below_price']:
            bearish_signals.append("Chikou below price")
        
        if conditions['cloud_bullish']:
            bullish_signals.append("Bullish cloud")
        if conditions['cloud_bearish']:
            bearish_signals.append("Bearish cloud")
        
        bullish_count = len(bullish_signals)
        bearish_count = len(bearish_signals)
        
        signal = 'HOLD'
        strength = 'VERY_LOW'
        reason = ''
        
        # Strong bullish (all conditions met)
        if bullish_count >= 3 and conditions['price_above_cloud'] and conditions['tenkan_above_kijun']:
            signal = 'BUY'
            strength = 'HIGH'
            reason = f"Strong Ichimoku bullish: {', '.join(bullish_signals)}"
        
        # Moderate bullish
        elif bullish_count >= 2:
            signal = 'BUY'
            strength = 'MODERATE'
            reason = f"Ichimoku bullish: {', '.join(bullish_signals)}"
        
        # Strong bearish
        elif bearish_count >= 3 and conditions['price_below_cloud'] and conditions['tenkan_below_kijun']:
            signal = 'SELL'
            strength = 'HIGH'
            reason = f"Strong Ichimoku bearish: {', '.join(bearish_signals)}"
        
        # Moderate bearish
        elif bearish_count >= 2:
            signal = 'SELL'
            strength = 'MODERATE'
            reason = f"Ichimoku bearish: {', '.join(bearish_signals)}"
        
        # In cloud = neutral
        elif conditions['price_in_cloud']:
            strength = 'VERY_LOW'
            reason = "Price inside Ichimoku cloud (neutral zone)"
        
        if signal != 'HOLD':
            log.info(f"☁️ Ichimoku Analysis:")
            log.info(f"   Price: ${current_price:,.2f}")
            log.info(f"   Cloud: ${cloud_bottom:,.2f} - ${cloud_top:,.2f} ({cloud_color})")
            log.info(f"   Tenkan: ${tenkan:,.2f}, Kijun: ${kijun:,.2f}")
            log.info(f"   Bullish signals: {bullish_count}, Bearish signals: {bearish_count}")
            log.info(f"   Signal: {signal} ({strength})")
        
        return {
            'signal': signal,
            'strength': strength,
            'reason': reason,
            'tenkan': tenkan,
            'kijun': kijun,
            'cloud_top': cloud_top,
            'cloud_bottom': cloud_bottom,
            'cloud_color': cloud_color,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'conditions': conditions
        }


if __name__ == "__main__":
    # Test with trending data
    base_price = 50000
    df = pd.DataFrame({
        'close': [base_price + i*100 + np.random.randint(-200, 200) for i in range(100)],
        'high': [base_price + i*100 + np.random.randint(0, 300) for i in range(100)],
        'low': [base_price + i*100 + np.random.randint(-300, 0) for i in range(100)],
    })
    
    strategy = IchimokuStrategy()
    result = strategy.analyze(df, df['close'].iloc[-1])
    
    print(f"\n☁️ Ichimoku Test:")
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Cloud: ${result['cloud_bottom']:,.2f} - ${result['cloud_top']:,.2f}")
    print(f"   Cloud Color: {result['cloud_color']}")
    print(f"   Bullish/Bearish: {result['bullish_count']}/{result['bearish_count']}")
