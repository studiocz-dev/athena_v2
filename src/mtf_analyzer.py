"""
Multi-Timeframe Analysis Module
Analyzes trading signals across multiple timeframes to improve signal quality.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging
from binance_client import BinanceFuturesClient
from strategies_enhanced import EnhancedTripleEMAStrategy, OptimizedStrategyFactory

logger = logging.getLogger(__name__)


class TimeframeStrength(Enum):
    """Signal strength based on timeframe alignment"""
    VERY_STRONG = 5  # All timeframes aligned
    STRONG = 4       # 3+ timeframes aligned
    MODERATE = 3     # 2 timeframes aligned
    WEAK = 2         # Only 1 timeframe signal
    NO_SIGNAL = 1    # No clear signal


class TrendDirection(Enum):
    """Trend direction across timeframes"""
    STRONG_BULLISH = "STRONG_BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL = "NEUTRAL"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG_BEARISH"


class MultiTimeframeAnalyzer:
    """
    Analyzes trading signals across multiple timeframes.
    
    Strategy:
    - Primary timeframe: 15m (for entries)
    - Confirmation timeframes: 1h, 4h (for trend direction)
    - Optional: Daily for major trend
    
    Signal is stronger when:
    1. All timeframes show same trend direction
    2. Higher timeframes confirm the primary signal
    3. Price is above/below key EMAs on higher timeframes
    """
    
    def __init__(
        self,
        binance_client: BinanceFuturesClient,
        primary_timeframe: str = "15m",
        confirmation_timeframes: List[str] = None
    ):
        """
        Initialize multi-timeframe analyzer.
        
        Args:
            binance_client: Binance client for fetching data
            primary_timeframe: Main timeframe for signal generation (default: 15m)
            confirmation_timeframes: List of higher timeframes for confirmation
        """
        self.client = binance_client
        self.primary_timeframe = primary_timeframe
        self.confirmation_timeframes = confirmation_timeframes or ["1h", "4h"]
        
        # Initialize strategy for each timeframe
        self.strategies = {
            tf: OptimizedStrategyFactory.create_balanced_strategy() 
            for tf in [primary_timeframe] + self.confirmation_timeframes
        }
        
        logger.info(
            f"Initialized MTF Analyzer - Primary: {primary_timeframe}, "
            f"Confirmation: {', '.join(self.confirmation_timeframes)}"
        )
    
    def analyze_symbol(
        self,
        symbol: str,
        limit: int = 200
    ) -> Dict:
        """
        Analyze a symbol across multiple timeframes.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            limit: Number of candles to fetch per timeframe
            
        Returns:
            Dict containing multi-timeframe analysis results
        """
        try:
            logger.info(f"Starting MTF analysis for {symbol}")
            
            # Fetch data for all timeframes
            timeframe_data = {}
            for timeframe in [self.primary_timeframe] + self.confirmation_timeframes:
                klines = self.client.get_klines(symbol, timeframe, limit=limit)
                df = self._prepare_dataframe(klines)
                timeframe_data[timeframe] = df
            
            # Analyze each timeframe
            timeframe_signals = {}
            for timeframe, df in timeframe_data.items():
                strategy = self.strategies[timeframe]
                signal = strategy.generate_signal(df)
                trend = self._determine_trend(df)
                
                timeframe_signals[timeframe] = {
                    'signal': signal,
                    'trend': trend,
                    'current_price': float(df['close'].iloc[-1]),
                    'ema_9': float(df['ema_9'].iloc[-1]) if 'ema_9' in df else None,
                    'ema_21': float(df['ema_21'].iloc[-1]) if 'ema_21' in df else None,
                    'ema_50': float(df['ema_50'].iloc[-1]) if 'ema_50' in df else None,
                }
            
            # Calculate signal strength
            signal_strength = self._calculate_signal_strength(timeframe_signals)
            
            # Get primary signal with enhanced confidence
            primary_signal = timeframe_signals[self.primary_timeframe]['signal']
            
            # Check if higher timeframes confirm the signal
            htf_confirmation = self._check_higher_timeframe_confirmation(
                primary_signal,
                timeframe_signals
            )
            
            # Overall trend assessment
            overall_trend = self._assess_overall_trend(timeframe_signals)
            
            # Final decision
            final_signal = self._make_final_decision(
                primary_signal,
                signal_strength,
                htf_confirmation,
                overall_trend
            )
            
            result = {
                'symbol': symbol,
                'timestamp': pd.Timestamp.now(),
                'primary_timeframe': self.primary_timeframe,
                'primary_signal': primary_signal,
                'final_signal': final_signal,
                'signal_strength': signal_strength,
                'htf_confirmation': htf_confirmation,
                'overall_trend': overall_trend,
                'timeframe_analysis': timeframe_signals,
                'current_price': timeframe_signals[self.primary_timeframe]['current_price'],
            }
            
            logger.info(
                f"{symbol} MTF Analysis - Signal: {final_signal}, "
                f"Strength: {signal_strength.name}, Trend: {overall_trend.name}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in MTF analysis for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'final_signal': 'HOLD'
            }
    
    def _prepare_dataframe(self, klines: List) -> pd.DataFrame:
        """Convert klines to DataFrame with OHLCV data."""
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        return df
    
    def _determine_trend(self, df: pd.DataFrame) -> TrendDirection:
        """
        Determine the trend direction based on EMA positions.
        
        Strong Bullish: Price > EMA9 > EMA21 > EMA50 (perfect alignment)
        Bullish: Price > EMA21 or EMA9 > EMA21
        Neutral: Mixed EMA positions
        Bearish: Price < EMA21 or EMA9 < EMA21
        Strong Bearish: Price < EMA9 < EMA21 < EMA50
        """
        if df.empty or len(df) < 50:
            return TrendDirection.NEUTRAL
        
        price = float(df['close'].iloc[-1])
        ema_9 = float(df['ema_9'].iloc[-1]) if 'ema_9' in df else None
        ema_21 = float(df['ema_21'].iloc[-1]) if 'ema_21' in df else None
        ema_50 = float(df['ema_50'].iloc[-1]) if 'ema_50' in df else None
        
        if not all([ema_9, ema_21, ema_50]):
            return TrendDirection.NEUTRAL
        
        # Check alignment
        if price > ema_9 > ema_21 > ema_50:
            return TrendDirection.STRONG_BULLISH
        elif price > ema_21 and ema_9 > ema_21:
            return TrendDirection.BULLISH
        elif price < ema_9 < ema_21 < ema_50:
            return TrendDirection.STRONG_BEARISH
        elif price < ema_21 and ema_9 < ema_21:
            return TrendDirection.BEARISH
        else:
            return TrendDirection.NEUTRAL
    
    def _calculate_signal_strength(
        self,
        timeframe_signals: Dict
    ) -> TimeframeStrength:
        """
        Calculate overall signal strength based on timeframe alignment.
        
        Returns:
            TimeframeStrength enum value
        """
        signals = [data['signal'] for data in timeframe_signals.values()]
        
        # Count bullish and bearish signals
        bullish_count = sum(1 for s in signals if s == 'BUY')
        bearish_count = sum(1 for s in signals if s == 'SELL')
        total_signals = len(signals)
        
        # All timeframes aligned
        if bullish_count == total_signals or bearish_count == total_signals:
            return TimeframeStrength.VERY_STRONG
        
        # 3+ timeframes aligned
        if bullish_count >= 3 or bearish_count >= 3:
            return TimeframeStrength.STRONG
        
        # 2 timeframes aligned
        if bullish_count >= 2 or bearish_count >= 2:
            return TimeframeStrength.MODERATE
        
        # Only 1 timeframe
        if bullish_count == 1 or bearish_count == 1:
            return TimeframeStrength.WEAK
        
        return TimeframeStrength.NO_SIGNAL
    
    def _check_higher_timeframe_confirmation(
        self,
        primary_signal: str,
        timeframe_signals: Dict
    ) -> bool:
        """
        Check if higher timeframes confirm the primary signal.
        
        Args:
            primary_signal: Signal from primary timeframe
            timeframe_signals: Signals from all timeframes
            
        Returns:
            True if at least one higher timeframe confirms
        """
        if primary_signal == 'HOLD':
            return False
        
        for timeframe in self.confirmation_timeframes:
            htf_signal = timeframe_signals[timeframe]['signal']
            htf_trend = timeframe_signals[timeframe]['trend']
            
            # Check if signal matches
            if htf_signal == primary_signal:
                return True
            
            # Check if trend aligns with signal direction
            if primary_signal == 'BUY':
                if htf_trend in [TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH]:
                    return True
            elif primary_signal == 'SELL':
                if htf_trend in [TrendDirection.BEARISH, TrendDirection.STRONG_BEARISH]:
                    return True
        
        return False
    
    def _assess_overall_trend(
        self,
        timeframe_signals: Dict
    ) -> TrendDirection:
        """
        Assess the overall trend across all timeframes.
        
        Higher timeframes have more weight in the assessment.
        """
        trends = [data['trend'] for data in timeframe_signals.values()]
        
        # Count trend directions
        strong_bullish = sum(1 for t in trends if t == TrendDirection.STRONG_BULLISH)
        bullish = sum(1 for t in trends if t == TrendDirection.BULLISH)
        strong_bearish = sum(1 for t in trends if t == TrendDirection.STRONG_BEARISH)
        bearish = sum(1 for t in trends if t == TrendDirection.BEARISH)
        
        total_bullish = strong_bullish + bullish
        total_bearish = strong_bearish + bearish
        
        # Strong trends
        if strong_bullish >= 2 or total_bullish >= 3:
            return TrendDirection.STRONG_BULLISH
        if strong_bearish >= 2 or total_bearish >= 3:
            return TrendDirection.STRONG_BEARISH
        
        # Moderate trends
        if total_bullish >= 2:
            return TrendDirection.BULLISH
        if total_bearish >= 2:
            return TrendDirection.BEARISH
        
        return TrendDirection.NEUTRAL
    
    def _make_final_decision(
        self,
        primary_signal: str,
        signal_strength: TimeframeStrength,
        htf_confirmation: bool,
        overall_trend: TrendDirection
    ) -> str:
        """
        Make final trading decision based on all factors.
        
        Rules:
        1. If signal strength is WEAK or NO_SIGNAL -> HOLD
        2. If no HTF confirmation and trend is opposite -> HOLD
        3. If signal strength is STRONG+ and HTF confirms -> Take signal
        4. If signal strength is MODERATE and trend aligns -> Take signal
        
        Args:
            primary_signal: Signal from primary timeframe
            signal_strength: Overall signal strength
            htf_confirmation: Whether higher timeframes confirm
            overall_trend: Overall trend direction
            
        Returns:
            Final signal: 'BUY', 'SELL', or 'HOLD'
        """
        # Weak or no signal
        if signal_strength in [TimeframeStrength.WEAK, TimeframeStrength.NO_SIGNAL]:
            return 'HOLD'
        
        # No primary signal
        if primary_signal == 'HOLD':
            return 'HOLD'
        
        # Check for conflicting signals
        if primary_signal == 'BUY':
            if overall_trend in [TrendDirection.STRONG_BEARISH, TrendDirection.BEARISH]:
                if not htf_confirmation:
                    return 'HOLD'  # Don't buy against the trend
        
        elif primary_signal == 'SELL':
            if overall_trend in [TrendDirection.STRONG_BULLISH, TrendDirection.BULLISH]:
                if not htf_confirmation:
                    return 'HOLD'  # Don't sell against the trend
        
        # Strong signals with confirmation
        if signal_strength in [TimeframeStrength.VERY_STRONG, TimeframeStrength.STRONG]:
            if htf_confirmation:
                return primary_signal
        
        # Moderate signals with trend alignment
        if signal_strength == TimeframeStrength.MODERATE:
            if primary_signal == 'BUY' and overall_trend in [
                TrendDirection.BULLISH, TrendDirection.STRONG_BULLISH
            ]:
                return 'BUY'
            elif primary_signal == 'SELL' and overall_trend in [
                TrendDirection.BEARISH, TrendDirection.STRONG_BEARISH
            ]:
                return 'SELL'
        
        # Default to hold if conditions not met
        return 'HOLD'
    
    def get_signal_summary(self, analysis: Dict) -> str:
        """
        Get a human-readable summary of the MTF analysis.
        
        Args:
            analysis: Result from analyze_symbol()
            
        Returns:
            Formatted summary string
        """
        if 'error' in analysis:
            return f"Error: {analysis['error']}"
        
        summary = f"""
Multi-Timeframe Analysis for {analysis['symbol']}
{'=' * 50}
Primary Signal ({analysis['primary_timeframe']}): {analysis['primary_signal']}
Final Decision: {analysis['final_signal']}
Signal Strength: {analysis['signal_strength'].name}
HTF Confirmation: {'✓' if analysis['htf_confirmation'] else '✗'}
Overall Trend: {analysis['overall_trend'].name}

Timeframe Breakdown:
"""
        for tf, data in analysis['timeframe_analysis'].items():
            summary += f"\n  {tf:>4} | Signal: {data['signal']:>4} | Trend: {data['trend'].name}"
        
        return summary
