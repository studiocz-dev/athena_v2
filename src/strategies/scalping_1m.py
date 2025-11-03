"""
1-Minute Scalping Strategy
Fast EMA crossovers for quick profits on 1-min charts
"""
import pandas as pd
import numpy as np
from typing import Dict
from logger import get_logger

log = get_logger('Scalping1M')


class Scalping1MStrategy:
    """
    1-Minute Scalping Strategy
    
    Strategy:
    - EMA 9/21 crossovers on 1-min chart
    - RSI confirmation (>50 for buy, <50 for sell)
    - Quick profit targets (0.3-0.5%)
    - Tight stop losses (0.15-0.2%)
    
    Ideal for:
    - High frequency trading
    - Quick momentum moves
    - 10-20 trades per day
    """
    
    def __init__(self, ema_fast: int = 9, ema_slow: int = 21, rsi_period: int = 14):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.rsi_period = rsi_period
        self.min_profit = 0.003  # 0.3%
        self.stop_loss = 0.0015  # 0.15%
        
    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate EMA"""
        return series.ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Analyze 1-min chart for scalping opportunities
        
        Args:
            df: 1-min OHLCV DataFrame
            current_price: Current market price
            
        Returns:
            Signal dictionary with entry, target, stop
        """
        if len(df) < max(self.ema_slow, self.rsi_period) + 5:
            return {
                'signal': 'HOLD',
                'strength': 'VERY_LOW',
                'reason': 'Insufficient 1-min data'
            }
        
        close = df['close']
        
        # Calculate EMAs
        ema9 = self.calculate_ema(close, self.ema_fast)
        ema21 = self.calculate_ema(close, self.ema_slow)
        
        # Calculate RSI
        rsi = self.calculate_rsi(close, self.rsi_period)
        
        # Current values
        ema9_curr = ema9.iloc[-1]
        ema21_curr = ema21.iloc[-1]
        ema9_prev = ema9.iloc[-2]
        ema21_prev = ema21.iloc[-2]
        rsi_curr = rsi.iloc[-1]
        rsi_prev = rsi.iloc[-2]
        
        signal = 'HOLD'
        strength = 'VERY_LOW'
        reason = ''
        entry = current_price
        target = 0
        stop = 0
        
        # Golden cross + RSI rising above 50
        if ema9_curr > ema21_curr and ema9_prev <= ema21_prev:
            if rsi_curr > 50 and rsi_curr > rsi_prev:
                signal = 'BUY'
                strength = 'HIGH'
                reason = f'EMA 9/21 golden cross + RSI rising ({rsi_curr:.1f})'
                target = current_price * (1 + self.min_profit)
                stop = current_price * (1 - self.stop_loss)
            elif rsi_curr > 45:
                signal = 'BUY'
                strength = 'MODERATE'
                reason = f'EMA golden cross, RSI neutral ({rsi_curr:.1f})'
                target = current_price * (1 + self.min_profit)
                stop = current_price * (1 - self.stop_loss)
        
        # Death cross + RSI falling below 50
        elif ema9_curr < ema21_curr and ema9_prev >= ema21_prev:
            if rsi_curr < 50 and rsi_curr < rsi_prev:
                signal = 'SELL'
                strength = 'HIGH'
                reason = f'EMA 9/21 death cross + RSI falling ({rsi_curr:.1f})'
                target = current_price * (1 - self.min_profit)
                stop = current_price * (1 + self.stop_loss)
            elif rsi_curr < 55:
                signal = 'SELL'
                strength = 'MODERATE'
                reason = f'EMA death cross, RSI neutral ({rsi_curr:.1f})'
                target = current_price * (1 - self.min_profit)
                stop = current_price * (1 + self.stop_loss)
        
        # Continuation signals (already in trend)
        elif ema9_curr > ema21_curr:
            # Uptrend
            if rsi_curr < 30:  # Oversold in uptrend
                signal = 'BUY'
                strength = 'MODERATE'
                reason = f'Oversold pullback in uptrend (RSI {rsi_curr:.1f})'
                target = current_price * (1 + self.min_profit)
                stop = current_price * (1 - self.stop_loss)
        
        elif ema9_curr < ema21_curr:
            # Downtrend
            if rsi_curr > 70:  # Overbought in downtrend
                signal = 'SELL'
                strength = 'MODERATE'
                reason = f'Overbought rally in downtrend (RSI {rsi_curr:.1f})'
                target = current_price * (1 - self.min_profit)
                stop = current_price * (1 + self.stop_loss)
        
        if signal != 'HOLD':
            log.info(f"⚡ 1-Min Scalp Signal:")
            log.info(f"   Signal: {signal} ({strength})")
            log.info(f"   Entry: ${entry:,.2f}")
            log.info(f"   Target: ${target:,.2f} ({'+' if signal=='BUY' else '-'}{self.min_profit*100:.1f}%)")
            log.info(f"   Stop: ${stop:,.2f} ({self.stop_loss*100:.2f}%)")
            log.info(f"   EMA9: ${ema9_curr:,.2f}, EMA21: ${ema21_curr:,.2f}")
            log.info(f"   RSI: {rsi_curr:.1f}")
        
        return {
            'signal': signal,
            'strength': strength,
            'reason': reason,
            'entry': entry,
            'target': target,
            'stop': stop,
            'ema9': ema9_curr,
            'ema21': ema21_curr,
            'rsi': rsi_curr,
            'risk_reward': 2.0  # 0.3% profit / 0.15% risk = 2:1 R/R
        }


if __name__ == "__main__":
    # Test with 1-min data
    base_price = 50000
    df = pd.DataFrame({
        'close': [base_price + i*10 + np.random.randint(-50, 50) for i in range(100)],
        'high': [base_price + i*10 + np.random.randint(0, 70) for i in range(100)],
        'low': [base_price + i*10 + np.random.randint(-70, 0) for i in range(100)],
        'volume': [np.random.randint(50, 200) for _ in range(100)]
    })
    
    strategy = Scalping1MStrategy()
    result = strategy.analyze(df, df['close'].iloc[-1])
    
    print(f"\n⚡ 1-Min Scalping Test:")
    print(f"   Signal: {result['signal']}")
    print(f"   Strength: {result['strength']}")
    print(f"   Reason: {result['reason']}")
    if result['signal'] != 'HOLD':
        print(f"   Entry: ${result['entry']:,.2f}")
        print(f"   Target: ${result['target']:,.2f}")
        print(f"   Stop: ${result['stop']:,.2f}")
        print(f"   Risk/Reward: {result['risk_reward']}:1")
