"""
Enhanced Signal Analyzer with Multi-Timeframe Support
"""

import pandas as pd
from typing import Dict, List, Optional
import logging
from binance_client import BinanceFuturesClient
from strategies_enhanced import EnhancedTripleEMAStrategy, OptimizedStrategyFactory
from mtf_analyzer import MultiTimeframeAnalyzer, TimeframeStrength, TrendDirection

logger = logging.getLogger(__name__)


class EnhancedSignalAnalyzer:
    """
    Enhanced Signal Analyzer with multi-timeframe analysis capabilities.
    
    Improvements over basic analyzer:
    1. Multi-timeframe signal confirmation
    2. Signal strength rating (1-5 stars)
    3. Enhanced entry/exit recommendations
    4. Dynamic stop loss and take profit based on ATR
    5. Risk assessment
    """
    
    def __init__(
        self,
        binance_client: BinanceFuturesClient,
        use_mtf: bool = True,
        primary_timeframe: str = "15m",
        confirmation_timeframes: List[str] = None
    ):
        """
        Initialize enhanced signal analyzer.
        
        Args:
            binance_client: Binance client for fetching data
            use_mtf: Whether to use multi-timeframe analysis (default: True)
            primary_timeframe: Primary timeframe for signals (default: 15m)
            confirmation_timeframes: Higher timeframes for confirmation
        """
        self.client = binance_client
        self.use_mtf = use_mtf
        self.primary_timeframe = primary_timeframe
        
        # Initialize enhanced strategy
        self.strategy = OptimizedStrategyFactory.create_balanced_strategy()
        
        # Initialize MTF analyzer if enabled
        if self.use_mtf:
            self.mtf_analyzer = MultiTimeframeAnalyzer(
                binance_client,
                primary_timeframe,
                confirmation_timeframes or ["1h", "4h"]
            )
            logger.info("Enhanced Signal Analyzer initialized with MTF support")
        else:
            self.mtf_analyzer = None
            logger.info("Enhanced Signal Analyzer initialized (single timeframe mode)")
    
    def analyze_symbol(
        self,
        symbol: str,
        timeframe: str = None,
        limit: int = 200
    ) -> Dict:
        """
        Analyze a symbol with enhanced signal generation.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            timeframe: Timeframe to analyze (uses primary if None)
            limit: Number of candles to fetch
            
        Returns:
            Dict containing comprehensive analysis
        """
        try:
            timeframe = timeframe or self.primary_timeframe
            
            # Use MTF analysis if enabled
            if self.use_mtf and self.mtf_analyzer:
                mtf_result = self.mtf_analyzer.analyze_symbol(symbol, limit)
                
                if 'error' in mtf_result:
                    return mtf_result
                
                # Get detailed data for the primary timeframe
                klines = self.client.get_klines(symbol, timeframe, limit=limit)
                df = self._prepare_dataframe(klines)
                df = self.strategy._calculate_indicators(df)
                
                # Calculate stop loss and take profit
                current_price = float(df['close'].iloc[-1])
                signal = mtf_result['final_signal']
                
                if signal != 'HOLD':
                    stop_loss, take_profit = self.strategy.calculate_stop_loss_take_profit(
                        current_price,
                        signal,
                        df
                    )
                else:
                    stop_loss, take_profit = None, None
                
                # Calculate signal stars (1-5 based on strength)
                stars = self._calculate_signal_stars(mtf_result['signal_strength'])
                
                # Build comprehensive result
                result = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal': signal,
                    'signal_strength': mtf_result['signal_strength'].name,
                    'stars': stars,
                    'current_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'mtf_confirmation': mtf_result['htf_confirmation'],
                    'overall_trend': mtf_result['overall_trend'].name,
                    'timeframe_analysis': mtf_result['timeframe_analysis'],
                    'risk_reward_ratio': self._calculate_risk_reward(
                        current_price, stop_loss, take_profit, signal
                    ) if signal != 'HOLD' else None,
                    'recommendation': self._generate_recommendation(mtf_result, stars),
                    'mtf_enabled': True
                }
                
                logger.info(
                    f"{symbol} Enhanced Analysis - Signal: {signal} ({stars}⭐), "
                    f"Strength: {result['signal_strength']}, "
                    f"Trend: {result['overall_trend']}"
                )
                
                return result
            
            else:
                # Single timeframe analysis
                klines = self.client.get_klines(symbol, timeframe, limit=limit)
                df = self._prepare_dataframe(klines)
                
                signal = self.strategy.generate_signal(df)
                current_price = float(df['close'].iloc[-1])
                
                if signal != 'HOLD':
                    stop_loss, take_profit = self.strategy.calculate_stop_loss_take_profit(
                        current_price,
                        signal,
                        df
                    )
                else:
                    stop_loss, take_profit = None, None
                
                result = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal': signal,
                    'signal_strength': 'MODERATE',
                    'stars': 3,
                    'current_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'mtf_confirmation': False,
                    'overall_trend': 'UNKNOWN',
                    'risk_reward_ratio': self._calculate_risk_reward(
                        current_price, stop_loss, take_profit, signal
                    ) if signal != 'HOLD' else None,
                    'recommendation': f"{signal} signal on {timeframe}",
                    'mtf_enabled': False
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'signal': 'HOLD'
            }
    
    def scan_multiple_symbols(
        self,
        symbols: List[str],
        timeframe: str = None,
        min_stars: int = 3
    ) -> List[Dict]:
        """
        Scan multiple symbols and return signals above minimum star rating.
        
        Args:
            symbols: List of trading pairs
            timeframe: Timeframe to analyze
            min_stars: Minimum star rating to include (default: 3)
            
        Returns:
            List of analysis results sorted by signal strength
        """
        results = []
        
        for symbol in symbols:
            try:
                analysis = self.analyze_symbol(symbol, timeframe)
                
                if 'error' not in analysis:
                    # Filter by minimum stars and non-HOLD signals
                    if analysis.get('stars', 0) >= min_stars and analysis['signal'] != 'HOLD':
                        results.append(analysis)
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by stars (descending) and then by signal strength
        results.sort(key=lambda x: (x.get('stars', 0), x.get('signal_strength', '')), reverse=True)
        
        logger.info(f"Scan complete: Found {len(results)} signals with {min_stars}+ stars")
        
        return results
    
    def _prepare_dataframe(self, klines: List) -> pd.DataFrame:
        """Convert klines to DataFrame."""
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        return df
    
    def _calculate_signal_stars(self, strength: TimeframeStrength) -> int:
        """
        Convert signal strength to star rating (1-5).
        
        VERY_STRONG: 5 stars
        STRONG: 4 stars
        MODERATE: 3 stars
        WEAK: 2 stars
        NO_SIGNAL: 1 star
        """
        return strength.value
    
    def _calculate_risk_reward(
        self,
        entry_price: float,
        stop_loss: Optional[float],
        take_profit: Optional[float],
        signal: str
    ) -> Optional[float]:
        """Calculate risk/reward ratio."""
        if not stop_loss or not take_profit:
            return None
        
        if signal == 'BUY':
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        else:  # SELL
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
        
        if risk <= 0:
            return None
        
        return reward / risk
    
    def _generate_recommendation(self, mtf_result: Dict, stars: int) -> str:
        """
        Generate a human-readable recommendation.
        
        Args:
            mtf_result: MTF analysis result
            stars: Signal star rating
            
        Returns:
            Recommendation string
        """
        signal = mtf_result['final_signal']
        strength = mtf_result['signal_strength'].name
        trend = mtf_result['overall_trend'].name
        htf_conf = mtf_result['htf_confirmation']
        
        if signal == 'HOLD':
            return "No clear signal. Wait for better setup."
        
        if stars >= 4:
            conf_text = "with higher timeframe confirmation" if htf_conf else "but no HTF confirmation"
            return (
                f"{'Strong' if stars == 5 else 'Good'} {signal} opportunity {conf_text}. "
                f"Overall trend is {trend}. Consider entering."
            )
        elif stars == 3:
            return (
                f"Moderate {signal} signal. Trend is {trend}. "
                f"{'HTF confirms' if htf_conf else 'HTF not confirming'}. Use caution."
            )
        else:
            return (
                f"Weak {signal} signal. Not recommended. "
                f"Wait for stronger confirmation."
            )
    
    def format_signal_details(self, analysis: Dict) -> str:
        """
        Format analysis result as a detailed string.
        
        Args:
            analysis: Analysis result from analyze_symbol()
            
        Returns:
            Formatted string with all details
        """
        if 'error' in analysis:
            return f"❌ Error: {analysis['error']}"
        
        signal_emoji = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '⚪'
        }
        
        emoji = signal_emoji.get(analysis['signal'], '⚪')
        stars = '⭐' * analysis.get('stars', 0)
        
        details = f"""
{emoji} {analysis['symbol']} - {analysis['signal']} {stars}
{'=' * 50}
Signal Strength: {analysis.get('signal_strength', 'N/A')}
Current Price: ${analysis['current_price']:.4f}
"""
        
        if analysis['signal'] != 'HOLD':
            details += f"""
Stop Loss: ${analysis['stop_loss']:.4f} ({self._calc_percent(analysis['current_price'], analysis['stop_loss']):.2f}%)
Take Profit: ${analysis['take_profit']:.4f} ({self._calc_percent(analysis['current_price'], analysis['take_profit']):.2f}%)
Risk/Reward: {analysis.get('risk_reward_ratio', 0):.2f}
"""
        
        if analysis.get('mtf_enabled'):
            details += f"""
Overall Trend: {analysis.get('overall_trend', 'N/A')}
HTF Confirmation: {'✅ Yes' if analysis.get('mtf_confirmation') else '❌ No'}

Timeframe Analysis:
"""
            for tf, data in analysis.get('timeframe_analysis', {}).items():
                details += f"  {tf:>4} | {data['signal']:>4} | {data['trend'].name}\n"
        
        details += f"\n📋 Recommendation:\n{analysis.get('recommendation', 'N/A')}\n"
        
        return details
    
    def _calc_percent(self, current: float, target: float) -> float:
        """Calculate percentage difference."""
        return ((target - current) / current) * 100
