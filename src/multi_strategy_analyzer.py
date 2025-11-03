"""
Multi-Strategy Signal Analyzer with Discord Integration
Combines all 8 trading strategies and sends comprehensive signals to Discord
"""

import pandas as pd
from typing import Dict, List, Optional
import logging
from binance_client import BinanceFuturesClient
from bybit_client import BybitFuturesClient
from multi_strategy import MultiStrategyManager
import config

logger = logging.getLogger(__name__)


class MultiStrategySignalAnalyzer:
    """
    Advanced Signal Analyzer that combines all 8 strategies:
    1. Pivot Points
    2. VWAP
    3. Bollinger Bands
    4. Stoch+RSI+MACD Triple Oscillator
    5. Fibonacci Retracements
    6. Ichimoku Cloud
    7. Parabolic SAR
    8. 1-Min Scalping (separate mode)
    
    Generates weighted signals and sends to Discord
    """
    
    def __init__(self, exchange_client, primary_timeframe: str = "15m"):
        """
        Initialize multi-strategy analyzer.
        
        Args:
            exchange_client: Binance or Bybit client
            primary_timeframe: Primary timeframe for analysis (default: 15m)
        """
        self.client = exchange_client
        self.primary_timeframe = primary_timeframe
        
        # Initialize multi-strategy manager
        self.multi_strategy = MultiStrategyManager()
        
        # Timeframes needed for different strategies
        self.required_timeframes = ['1m', '15m', '1h', '4h', '1d']
        
        logger.info("Multi-Strategy Signal Analyzer initialized with 8 strategies")
    
    def analyze_symbol(
        self,
        symbol: str,
        include_scalping: bool = False
    ) -> Dict:
        """
        Analyze a symbol using all strategies.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            include_scalping: Whether to include 1-min scalping analysis
            
        Returns:
            Dict containing comprehensive multi-strategy analysis
        """
        try:
            logger.info(f"Analyzing {symbol} with multi-strategy system...")
            
            # Fetch data for all required timeframes
            klines_data = {}
            for tf in self.required_timeframes:
                try:
                    if tf == '1m':
                        limit = 100  # Last 100 minutes
                    elif tf == '15m':
                        limit = 100  # Last 25 hours
                    elif tf == '1h':
                        limit = 100  # Last 100 hours (~4 days)
                    elif tf == '4h':
                        limit = 100  # Last 400 hours (~17 days)
                    else:  # 1d
                        limit = 50   # Last 50 days
                    
                    klines = self.client.get_klines(symbol, tf, limit=limit)
                    klines_data[tf] = self._prepare_dataframe(klines)
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch {tf} data for {symbol}: {e}")
                    klines_data[tf] = None
            
            # Verify we have at least 15m data (primary timeframe)
            if klines_data.get('15m') is None or len(klines_data['15m']) == 0:
                return {
                    'symbol': symbol,
                    'error': 'Failed to fetch primary timeframe data',
                    'signal': 'HOLD'
                }
            
            # Get current price and RSI from primary timeframe
            df_primary = klines_data['15m']
            current_price = float(df_primary['close'].iloc[-1])
            
            # Calculate RSI if not already present
            if 'rsi' not in df_primary.columns:
                df_primary = self._calculate_rsi(df_primary)
            
            rsi = float(df_primary['rsi'].iloc[-1]) if 'rsi' in df_primary.columns else 50.0
            
            # Run multi-strategy analysis
            multi_result = self.multi_strategy.analyze_all(
                symbol=symbol,
                klines_data=klines_data,
                current_price=current_price,
                rsi=rsi
            )
            
            # Calculate entry/exit levels based on final signal
            signal = multi_result['signal']  # Changed from 'final_signal'
            
            if signal != 'HOLD':
                stop_loss, take_profit = self._calculate_levels(
                    current_price,
                    signal,
                    df_primary
                )
                risk_reward = self._calculate_risk_reward(
                    current_price, stop_loss, take_profit, signal
                )
            else:
                stop_loss, take_profit, risk_reward = None, None, None
            
            # Build comprehensive result
            result = {
                'symbol': symbol,
                'timeframe': self.primary_timeframe,
                'current_price': current_price,
                'rsi': rsi,
                
                # Multi-strategy results
                'signal': signal,  # Use 'signal' for consistency
                'final_signal': signal,  # Also keep 'final_signal' for compatibility
                'signal_strength': multi_result['strength'],  # Changed from 'signal_strength'
                'confidence': multi_result['confidence'],
                'consensus': multi_result['confidence'],  # Same as confidence
                
                # Strategy breakdown (from strategy_breakdown)
                'strategy_signals': {},  # Will populate below
                'buy_score': multi_result['buy_score'],
                'sell_score': multi_result['sell_score'],
                'hold_score': multi_result['hold_score'],
                
                # Entry/exit levels
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward': risk_reward,
                
                # Stars (1-5 based on consensus)
                'stars': self._calculate_stars(multi_result['confidence']),  # Use confidence
                
                # Recommendation
                'recommendation': self._generate_recommendation(multi_result, signal),
                
                # System info
                'strategies_used': multi_result['total_strategies'],  # Changed from 'strategies_used'
                'total_strategies': 7,  # Not including scalping
                'multi_strategy_enabled': True
            }
            
            # Convert strategy_breakdown to strategy_signals format
            for item in multi_result.get('strategy_breakdown', []):
                result['strategy_signals'][item['strategy']] = {
                    'signal': item['signal'],
                    'strength': item['strength']
                }
            
            logger.info(
                f"{symbol} Multi-Strategy Analysis Complete - "
                f"Signal: {signal} ({result['stars']}⭐), "
                f"Strength: {result['signal_strength']}, "
                f"Consensus: {result['consensus']:.1f}%, "
                f"Confidence: {result['confidence']:.1f}%"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
            return {
                'symbol': symbol,
                'error': str(e),
                'signal': 'HOLD',
                'final_signal': 'HOLD'
            }
    
    def scan_multiple_symbols(
        self,
        symbols: List[str],
        min_confidence: float = 60.0,
        min_stars: int = 3
    ) -> List[Dict]:
        """
        Scan multiple symbols and return strong signals.
        
        Args:
            symbols: List of trading pairs
            min_confidence: Minimum confidence percentage (default: 60%)
            min_stars: Minimum star rating (default: 3)
            
        Returns:
            List of analysis results sorted by confidence
        """
        results = []
        
        for symbol in symbols:
            try:
                analysis = self.analyze_symbol(symbol)
                
                if 'error' not in analysis:
                    # Filter by confidence, stars, and non-HOLD signals
                    if (analysis.get('confidence', 0) >= min_confidence and
                        analysis.get('stars', 0) >= min_stars and
                        analysis['final_signal'] != 'HOLD'):
                        results.append(analysis)
                        
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by confidence (descending) then by stars
        results.sort(
            key=lambda x: (x.get('confidence', 0), x.get('stars', 0)),
            reverse=True
        )
        
        logger.info(
            f"Scan complete: Found {len(results)} signals with "
            f"{min_confidence}%+ confidence and {min_stars}+ stars"
        )
        
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
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate RSI indicator."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def _calculate_levels(
        self,
        current_price: float,
        signal: str,
        df: pd.DataFrame
    ) -> tuple:
        """
        Calculate stop loss and take profit levels.
        
        Uses ATR-based approach:
        - Stop Loss: 1.5 ATR
        - Take Profit: 3 ATR (2:1 R/R)
        """
        # Calculate ATR if not present
        if 'atr' not in df.columns:
            df['atr'] = self._calculate_atr(df)
        
        atr = float(df['atr'].iloc[-1])
        
        if signal == 'BUY':
            stop_loss = current_price - (1.5 * atr)
            take_profit = current_price + (3.0 * atr)
        else:  # SELL
            stop_loss = current_price + (1.5 * atr)
            take_profit = current_price - (3.0 * atr)
        
        return stop_loss, take_profit
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def _calculate_risk_reward(
        self,
        entry: float,
        stop_loss: float,
        take_profit: float,
        signal: str
    ) -> float:
        """Calculate risk/reward ratio."""
        if signal == 'BUY':
            risk = entry - stop_loss
            reward = take_profit - entry
        else:  # SELL
            risk = stop_loss - entry
            reward = entry - take_profit
        
        return reward / risk if risk > 0 else 0
    
    def _calculate_stars(self, consensus: float) -> int:
        """
        Convert consensus percentage to star rating (1-5).
        
        85%+: 5 stars (very strong)
        70-85%: 4 stars (strong)
        60-70%: 3 stars (moderate)
        50-60%: 2 stars (weak)
        <50%: 1 star (very weak)
        """
        if consensus >= 85:
            return 5
        elif consensus >= 70:
            return 4
        elif consensus >= 60:
            return 3
        elif consensus >= 50:
            return 2
        else:
            return 1
    
    def _generate_recommendation(self, multi_result: Dict, signal: str) -> str:
        """Generate human-readable recommendation."""
        confidence = multi_result['confidence']  # Confidence is the consensus
        consensus = confidence  # Use confidence as consensus
        strategies = multi_result['total_strategies']
        
        if signal == 'HOLD':
            return (
                f"No clear consensus signal. {strategies} strategies analyzed. "
                f"Wait for better setup."
            )
        
        if consensus >= 85:
            return (
                f"⭐⭐⭐⭐⭐ VERY STRONG {signal} - {consensus:.0f}% consensus "
                f"from {strategies} strategies. High conviction entry!"
            )
        elif consensus >= 70:
            return (
                f"⭐⭐⭐⭐ STRONG {signal} - {consensus:.0f}% consensus. "
                f"Good entry opportunity with {confidence:.0f}% confidence."
            )
        elif consensus >= 60:
            return (
                f"⭐⭐⭐ MODERATE {signal} - {consensus:.0f}% consensus. "
                f"Decent setup but use caution."
            )
        else:
            return (
                f"⭐⭐ WEAK {signal} - Only {consensus:.0f}% consensus. "
                f"Not recommended. Wait for stronger signal."
            )
    
    def format_discord_message(self, analysis: Dict) -> str:
        """
        Format analysis as Discord-ready message with emojis and formatting.
        
        Args:
            analysis: Analysis result from analyze_symbol()
            
        Returns:
            Formatted Discord message string
        """
        if 'error' in analysis:
            return f"❌ **Error analyzing {analysis['symbol']}:** {analysis['error']}"
        
        signal = analysis['final_signal']
        
        if signal == 'HOLD':
            return None  # Don't send HOLD signals to Discord
        
        # Signal emoji
        emoji = '🟢' if signal == 'BUY' else '🔴'
        stars = '⭐' * analysis['stars']
        
        # Build message
        msg = f"""
{emoji} **{analysis['symbol']} - {signal} SIGNAL** {stars}

**Signal Strength:** {analysis['signal_strength']}
**Confidence:** {analysis['confidence']:.1f}%
**Consensus:** {analysis['consensus']:.1f}% ({analysis['strategies_used']}/{analysis['total_strategies']} strategies)

**Price:** ${analysis['current_price']:,.2f}
**RSI:** {analysis['rsi']:.1f}

**Entry Levels:**
└ Stop Loss: ${analysis['stop_loss']:,.2f} ({self._calc_percent(analysis['current_price'], analysis['stop_loss']):.2f}%)
└ Take Profit: ${analysis['take_profit']:,.2f} ({self._calc_percent(analysis['current_price'], analysis['take_profit']):.2f}%)
└ Risk/Reward: {analysis['risk_reward']:.2f}:1

**Strategy Breakdown:**"""
        
        # Add individual strategy signals
        for strategy, data in analysis['strategy_signals'].items():
            sig_emoji = '🟢' if data['signal'] == 'BUY' else ('🔴' if data['signal'] == 'SELL' else '⚪')
            msg += f"\n└ {sig_emoji} **{strategy}:** {data['signal']} ({data['strength']})"
        
        msg += f"\n\n**Scoring:**"
        msg += f"\n└ Buy: {analysis['buy_score']:.2f} | Sell: {analysis['sell_score']:.2f} | Hold: {analysis['hold_score']:.2f}"
        
        msg += f"\n\n📋 **Recommendation:**\n{analysis['recommendation']}"
        
        msg += f"\n\n🕒 *{self.primary_timeframe} timeframe analysis*"
        
        return msg
    
    def _calc_percent(self, current: float, target: float) -> float:
        """Calculate percentage difference."""
        return ((target - current) / current) * 100
