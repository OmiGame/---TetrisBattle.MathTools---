"""
战斗模拟器主模块
"""

from .battle_engine import BattleEngine
from .visualization.visualization import BattleVisualizer
from .analysis import BattleAnalysis
from .statistics import BattleStatistics
from .global_config import (
    SIMULATOR_CONFIG,
    BATTLE_SYSTEM_CONFIG,
    BATTLE_ENGINE_CONFIG,
    VISUALIZATION_CONFIG,
    STATISTICS_CONFIG,
    ANALYSIS_CONFIG
)

__all__ = [
    'BattleEngine',
    'BattleVisualizer',
    'BattleAnalyzer',
    'BattleStatistics',
    'SIMULATOR_CONFIG',
    'BATTLE_SYSTEM_CONFIG',
    'BATTLE_ENGINE_CONFIG',
    'VISUALIZATION_CONFIG',
    'STATISTICS_CONFIG',
    'ANALYSIS_CONFIG'
] 