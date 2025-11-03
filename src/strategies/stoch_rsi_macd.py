"""
Stochastic + RSI + MACD Triple Oscillator Strategy
High-conviction signals when all three indicators align
"""
import pandas as pd
import numpy as np
from typing import Dict
from logger import get_logger

log = get_logger('StochRSIMacd')


class StochRSIMacdStrategy:
    """
    Triple Oscillator Confirmation Strategy
    
    Combines:
    - Stochastic Oscillator (14,3,3) - Momentum
    - RSI (14) - Overbought/Oversold
    - MACD (12,26,9) - Trend strength
    
    Signals:
    - HIGH: All 3 bullish/bearish
    - MODERATE: 2 out of 3 align
    - LOW: Only 1 indicator
    """
    
    def __init__(self):
        self.stoch_period = 14
        self.stoch_k = 3
        self.stoch_d = 3
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        
    def calculate_stochastic(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator"""
        low_min = df['low'].rolling(window=self.stoch_period).min()
        high_max = df['high'].rolling(window=self.stoch_period).max()
        
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        k = k.rolling(window=self.stoch_k).mean()
        d = k.rolling(window=self.stoch_d).mean()
        
        return {'k': k, 'd': d}
    
    def calculate_rsi(self, series: pd.Series) -> pd.Series:
        """Calculate RSI"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, series: pd.Series) -> Dict[str, pd.Series]:
        """Calculate MACD"""
        ema_fast = series.ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = series.ewm(span=self.macd_slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=self.macd_signal, adjust=False).mean()
        histogram = macd - signal
        
        return {
            'macd': macd,
            'signal': signal,
            'histogram': histogram
        }
    
    def analyze(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Analyze with triple oscillator confirmation
        
        Args:
            df: OHLCV DataFrame (15-min or 1-hour recommended)
            current_price: Current market price
            
        Returns:
            Signal dictionary with strength based on alignment
        """
        min_length = max(self.stoch_period, self.rsi_period, self.macd_slow) + 20
        if len(df) < min_length:
            return {
                'signal': 'HOLD',
                'strength': 'VERY_LOW',
                'reason': 'Insufficient data for triple oscillator'
            }
        
        close = df['close']
        
        # Calculate all indicators
        stoch = self.calculate_stochastic(df)
        rsi = self.calculate_rsi(close)
        macd_data = self.calculate_macd(close)
        
        # Current values
        stoch_k = stoch['k'].iloc[-1]
        stoch_d = stoch['d'].iloc[-1]
        stoch_k_prev = stoch['k'].iloc[-2]
        stoch_d_prev = stoch['d'].iloc[-2]
        
        rsi_curr = rsi.iloc[-1]
        rsi_prev = rsi.iloc[-2]
        
        macd = macd_data['macd'].iloc[-1]
        macd_signal = macd_data['signal'].iloc[-1]
        macd_hist = macd_data['histogram'].iloc[-1]
        macd_hist_prev = macd_data['histogram'].iloc[-2]
        
        # Determine each indicator's signal
        bullish_signals = []
        bearish_signals = []
        
        # 1. Stochastic
        if stoch_k < 20 and stoch_k > stoch_d and stoch_k_prev <= stoch_d_prev:
            bullish_signals.append(f"Stoch oversold crossover (K={stoch_k:.1f})")
        elif stoch_k < 30:
            bullish_signals.append(f"Stoch oversold zone (K={stoch_k:.1f})")
        
        if stoch_k > 80 and stoch_k < stoch_d and stoch_k_prev >= stoch_d_prev:
            bearish_signals.append(f"Stoch overbought crossunder (K={stoch_k:.1f})")
        elif stoch_k > 70:
            bearish_signals.append(f"Stoch overbought zone (K={stoch_k:.1f})")
        
        # 2. RSI
        if rsi_curr < 30:
            bullish_signals.append(f"RSI oversold ({rsi_curr:.1f})")
        elif rsi_curr < 40 and rsi_curr > rsi_prev:
            bullish_signals.append(f"RSI rising from oversold ({rsi_curr:.1f})")
        
        if rsi_curr > 70:
            bearish_signals.append(f"RSI overbought ({rsi_curr:.1f})")
        elif rsi_curr > 60 and rsi_curr < rsi_prev:
            bearish_signals.append(f"RSI falling from overbought ({rsi_curr:.1f})")
        
        # 3. MACD
        if macd > macd_signal and macd_hist > 0:
            bullish_signals.append(f"MACD bullish (hist={macd_hist:.2f})")
        elif macd_hist > 0 and macd_hist > macd_hist_prev:
            bullish_signals.append(f"MACD histogram rising")
        
        if macd < macd_signal and macd_hist < 0:
            bearish_signals.append(f"MACD bearish (hist={macd_hist:.2f})")
        elif macd_hist < 0 and macd_hist < macd_hist_prev:
            bearish_signals.append(f"MACD histogram falling")
        
        # Determine signal strength
        bullish_count = len(bullish_signals)
        bearish_count = len(bearish_signals)
        
        signal = 'HOLD'
        strength = 'VERY_LOW'
        reason = ''
        
        if bullish_count >= 3:
            signal = 'BUY'
            strength = 'HIGH'
            reason = "All 3 oscillators bullish: " + ", ".join(bullish_signals)
        elif bullish_count == 2:
            signal = 'BUY'
            strength = 'MODERATE'
            reason = "2/3 oscillators bullish: " + ", ".join(bullish_signals)
        elif bullish_count == 1:
            strength = 'LOW'
            reason = "1/3 bullish: " + bullish_signals[0]
        
        if bearish_count >= 3:
            signal = 'SELL'
            strength = 'HIGH'
            reason = "All 3 oscillators bearish: " + ", ".join(bearish_signals)
        elif bearish_count == 2:
            signal = 'SELL'
            strength = 'MODERATE'
            reason = "2/3 oscillators bearish: " + ", ".join(bearish_signals)
        elif bearish_count == 1 and bullish_count == 0:
            strength = 'LOW'
            reason = "1/3 bearish: " + bearish_signals[0]
        
        # If both bullish and bearish signals, use the stronger one
        if bullish_count > 0 and bearish_count > 0:
            if bullish_count > bearish_count:
                signal = 'BUY'
                strength = 'LOW'
                reason = f"Mixed signals, {bullish_count} bullish vs {bearish_count} bearish"
            elif bearish_count > bullish_count:
                signal = 'SELL'
                strength = 'LOW'
                reason = f"Mixed signals, {bearish_count} bearish vs {bullish_count} bullish"
            else:
                signal = 'HOLD'
                strength = 'VERY_LOW'
                reason = "Conflicting oscillator signals"
        
        if signal != 'HOLD' and strength in ['HIGH', 'MODERATE']:
            log.info(f"🎯 Triple Oscillator Analysis:")
            log.info(f"   Stochastic: K={stoch_k:.1f}, D={stoch_d:.1f}")
            log.info(f"   RSI: {rsi_curr:.1f}")
            log.info(f"   MACD: {macd:.2f} vs Signal {macd_signal:.2f}")
            log.info(f"   Signal: {signal} ({strength})")
            log.info(f"   Reason: {reason}")
        
        return {
            'signal': signal,
            'strength': strength,
            'reason': reason,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d,
            'rsi': rsi_curr,
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_histogram': macd_hist,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count
        }


if __name__ == "__main__":
    # Test
    base_price = 50000
    df = pd.DataFrame({
        'close': [base_price + i*50 + np.random.randint(-200, 200) for i in range(100)],
        'high': [base_price + i*50 + np.random.randint(0, 300) for i in range(100)],
        'low': [base_price + i*50 + np.random.randint(-300, 0) for i in range(100)],
        'volume': [np.random.randint(100, 1000) for _ in range(100)]
    })
    
    strategy = StochRSIMacdStrategy()
    result = strategy.analyze(df, df['close'].iloc[-1])
    
    print(f"\n🎯 Triple Oscillator Test:")
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reason: {result['reason']}")
    print(f"   Stochastic K: {result['stoch_k']:.1f}")
    print(f"   RSI: {result['rsi']:.1f}")
    print(f"   MACD Hist: {result['macd_histogram']:.2f}")
    print(f"   Bullish/Bearish: {result['bullish_count']}/{result['bearish_count']}")
