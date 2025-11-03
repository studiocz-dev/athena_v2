"""
Trading Strategies Module
Contains all implemented trading strategies
"""

from .pivot_points import PivotPointsStrategy
from .vwap import VWAPStrategy
from .bollinger_bands import BollingerBandsStrategy
from .scalping_1m import Scalping1MStrategy
from .stoch_rsi_macd import StochRSIMacdStrategy
from .fibonacci import FibonacciStrategy
from .ichimoku import IchimokuStrategy
from .parabolic_sar import ParabolicSARStrategy

__all__ = [
    'PivotPointsStrategy',
    'VWAPStrategy',
    'BollingerBandsStrategy',
    'Scalping1MStrategy',
    'StochRSIMacdStrategy',
    'FibonacciStrategy',
    'IchimokuStrategy',
    'ParabolicSARStrategy'
]

__version__ = '2.0.0'
__author__ = 'Athena Trading Bot'
