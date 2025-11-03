"""
Multi-Strategy Manager
Combines all strategies with weighted scoring
"""
import pandas as pd
from typing import Dict, List
from logger import get_logger

# Import all strategies
from strategies.pivot_points import PivotPointsStrategy
from strategies.vwap import VWAPStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.scalping_1m import Scalping1MStrategy
from strategies.stoch_rsi_macd import StochRSIMacdStrategy
from strategies.fibonacci import FibonacciStrategy
from strategies.ichimoku import IchimokuStrategy
from strategies.parabolic_sar import ParabolicSARStrategy

log = get_logger('MultiStrategy')


class MultiStrategyManager:
    """
    Manages multiple trading strategies with weighted scoring
    
    Combines signals from all strategies to generate a final decision
    Each strategy has a configurable weight based on effectiveness
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize multi-strategy manager
        
        Args:
            config: Dictionary with strategy weights and settings
        """
        # Default configuration
        self.config = config or {
            'weights': {
                'PIVOT_POINTS': 0.20,
                'VWAP': 0.15,
                'BOLLINGER': 0.15,
                'STOCH_RSI_MACD': 0.20,
                'FIBONACCI': 0.10,
                'ICHIMOKU': 0.10,
                'PARABOLIC_SAR': 0.10
            },
            'min_strength': 'MODERATE',  # Minimum strength to consider
            'min_score': 0.5,  # Minimum weighted score to generate signal (0-1)
            'require_consensus': False  # If True, majority of strategies must agree
        }
        
        # Initialize all strategies
        self.strategies = {
            'PIVOT_POINTS': PivotPointsStrategy(),
            'VWAP': VWAPStrategy(),
            'BOLLINGER': BollingerBandsStrategy(),
            'STOCH_RSI_MACD': StochRSIMacdStrategy(),
            'FIBONACCI': FibonacciStrategy(),
            'ICHIMOKU': IchimokuStrategy(),
            'PARABOLIC_SAR': ParabolicSARStrategy()
        }
        
        # Strength to numeric score mapping
        self.strength_scores = {
            'VERY_LOW': 0.0,
            'LOW': 0.25,
            'MODERATE': 0.5,
            'HIGH': 0.75,
            'VERY_HIGH': 1.0
        }
        
    def analyze_all(self, symbol: str, klines_data: Dict[str, pd.DataFrame], 
                   current_price: float, rsi: float = 50) -> Dict:
        """
        Run all strategies and combine results
        
        Args:
            symbol: Trading symbol
            klines_data: Dictionary with DataFrames for different timeframes
                        Keys: '1m', '15m', '1h', '4h', '1d'
            current_price: Current market price
            rsi: Current RSI value
            
        Returns:
            Combined signal with detailed breakdown
        """
        results = {}
        
        # Run each strategy
        log.info(f"\n{'='*60}")
        log.info(f"🎯 Multi-Strategy Analysis: {symbol}")
        log.info(f"{'='*60}")
        
        # 1. Pivot Points (needs daily data)
        if '1d' in klines_data and len(klines_data['1d']) > 10:
            results['PIVOT_POINTS'] = self.strategies['PIVOT_POINTS'].analyze(
                klines_data['1d'], current_price, rsi
            )
        
        # 2. VWAP (needs intraday data)
        if '15m' in klines_data and len(klines_data['15m']) > 50:
            results['VWAP'] = self.strategies['VWAP'].analyze(
                klines_data['15m'], current_price
            )
        
        # 3. Bollinger Bands
        if '15m' in klines_data and len(klines_data['15m']) > 30:
            results['BOLLINGER'] = self.strategies['BOLLINGER'].analyze(
                klines_data['15m'], current_price
            )
        
        # 4. Stoch + RSI + MACD
        if '1h' in klines_data and len(klines_data['1h']) > 50:
            results['STOCH_RSI_MACD'] = self.strategies['STOCH_RSI_MACD'].analyze(
                klines_data['1h'], current_price
            )
        
        # 5. Fibonacci
        if '4h' in klines_data and len(klines_data['4h']) > 50:
            results['FIBONACCI'] = self.strategies['FIBONACCI'].analyze(
                klines_data['4h'], current_price
            )
        
        # 6. Ichimoku
        if '4h' in klines_data and len(klines_data['4h']) > 80:
            results['ICHIMOKU'] = self.strategies['ICHIMOKU'].analyze(
                klines_data['4h'], current_price
            )
        
        # 7. Parabolic SAR
        if '1h' in klines_data and len(klines_data['1h']) > 30:
            results['PARABOLIC_SAR'] = self.strategies['PARABOLIC_SAR'].analyze(
                klines_data['1h'], current_price
            )
        
        # Combine results
        combined = self.combine_signals(results)
        
        # Log summary
        log.info(f"\n📊 Strategy Results:")
        for name, result in results.items():
            signal = result.get('signal', 'HOLD')
            strength = result.get('strength', 'VERY_LOW')
            log.info(f"   {name:20s}: {signal:4s} ({strength})")
        
        log.info(f"\n🎯 Combined Signal:")
        log.info(f"   Final: {combined['signal']} ({combined['strength']})")
        log.info(f"   Score: {combined['score']:.2f}")
        log.info(f"   Consensus: {combined['buy_count']} BUY, {combined['sell_count']} SELL, {combined['hold_count']} HOLD")
        log.info(f"   Confidence: {combined['confidence']:.1f}%")
        
        return combined
    
    def combine_signals(self, results: Dict[str, Dict]) -> Dict:
        """
        Combine signals from all strategies using weighted scoring
        
        Args:
            results: Dictionary of strategy results
            
        Returns:
            Combined signal dictionary
        """
        buy_score = 0.0
        sell_score = 0.0
        hold_score = 0.0
        
        buy_count = 0
        sell_count = 0
        hold_count = 0
        
        total_weight = 0.0
        strategy_breakdown = []
        
        for strategy_name, result in results.items():
            signal = result.get('signal', 'HOLD')
            strength = result.get('strength', 'VERY_LOW')
            reason = result.get('reason', '')
            
            # Get weight for this strategy
            weight = self.config['weights'].get(strategy_name, 0.1)
            total_weight += weight
            
            # Convert strength to numeric score
            strength_score = self.strength_scores.get(strength, 0.0)
            
            # Calculate weighted score
            weighted_score = weight * strength_score
            
            # Add to appropriate category
            if signal == 'BUY':
                buy_score += weighted_score
                buy_count += 1
            elif signal == 'SELL':
                sell_score += weighted_score
                sell_count += 1
            else:
                hold_score += weighted_score
                hold_count += 1
            
            strategy_breakdown.append({
                'strategy': strategy_name,
                'signal': signal,
                'strength': strength,
                'weight': weight,
                'weighted_score': weighted_score,
                'reason': reason
            })
        
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
            hold_score /= total_weight
        
        # Determine final signal
        max_score = max(buy_score, sell_score, hold_score)
        
        if max_score < self.config['min_score']:
            final_signal = 'HOLD'
            final_strength = 'VERY_LOW'
            reason = f"Insufficient score ({max_score:.2f} < {self.config['min_score']})"
        
        elif buy_score == max_score:
            final_signal = 'BUY'
            # Determine strength based on score
            if buy_score >= 0.75:
                final_strength = 'HIGH'
            elif buy_score >= 0.5:
                final_strength = 'MODERATE'
            else:
                final_strength = 'LOW'
            reason = f"Buy score: {buy_score:.2f} ({buy_count} strategies)"
        
        elif sell_score == max_score:
            final_signal = 'SELL'
            if sell_score >= 0.75:
                final_strength = 'HIGH'
            elif sell_score >= 0.5:
                final_strength = 'MODERATE'
            else:
                final_strength = 'LOW'
            reason = f"Sell score: {sell_score:.2f} ({sell_count} strategies)"
        
        else:
            final_signal = 'HOLD'
            final_strength = 'LOW'
            reason = f"Hold score: {hold_score:.2f}"
        
        # Calculate confidence (agreement percentage)
        total_strategies = buy_count + sell_count + hold_count
        if total_strategies > 0:
            if final_signal == 'BUY':
                confidence = (buy_count / total_strategies) * 100
            elif final_signal == 'SELL':
                confidence = (sell_count / total_strategies) * 100
            else:
                confidence = (hold_count / total_strategies) * 100
        else:
            confidence = 0
        
        # Check consensus requirement
        if self.config['require_consensus']:
            consensus_threshold = 0.6  # 60% must agree
            if confidence < consensus_threshold * 100:
                final_signal = 'HOLD'
                final_strength = 'LOW'
                reason = f"No consensus (only {confidence:.0f}% agree)"
        
        return {
            'signal': final_signal,
            'strength': final_strength,
            'reason': reason,
            'score': max_score,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'hold_score': hold_score,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'hold_count': hold_count,
            'confidence': confidence,
            'strategy_breakdown': strategy_breakdown,
            'total_strategies': total_strategies
        }
    
    def get_strategy_summary(self, combined_result: Dict) -> str:
        """Format strategy breakdown as text"""
        text = "📊 Strategy Breakdown:\n\n"
        
        for item in combined_result['strategy_breakdown']:
            signal_emoji = "🟢" if item['signal'] == 'BUY' else "🔴" if item['signal'] == 'SELL' else "⚪"
            text += f"{signal_emoji} **{item['strategy']}** ({item['strength']})\n"
            text += f"   Weight: {item['weight']:.2f}, Score: {item['weighted_score']:.3f}\n"
            text += f"   {item['reason']}\n\n"
        
        text += f"**Final Decision:**\n"
        text += f"Signal: {combined_result['signal']} ({combined_result['strength']})\n"
        text += f"Score: {combined_result['score']:.2f}\n"
        text += f"Confidence: {combined_result['confidence']:.0f}%\n"
        
        return text


if __name__ == "__main__":
    # Test
    print("🎯 Multi-Strategy Manager initialized")
    print(f"   Strategies loaded: 7")
    print(f"   Configuration: Default weights")
    
    manager = MultiStrategyManager()
    
    print("\n📊 Strategy Weights:")
    for name, weight in manager.config['weights'].items():
        print(f"   {name:20s}: {weight:.2f}")
    
    print("\n✅ Multi-strategy manager ready!")
