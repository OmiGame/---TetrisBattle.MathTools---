"""
战斗模拟配置模块
"""

from typing import Dict, Any

# 战斗引擎配置
BATTLE_ENGINE_CONFIG: Dict[str, Any] = {
    'max_turns': 100,  # 最大回合数
    'random_seed': None,  # 随机种子
    'log_level': 'INFO',  # 日志级别
}

# 可视化配置
VISUALIZATION_CONFIG: Dict[str, Any] = {
    'screen_width': 800,
    'screen_height': 600,
    'fps': 60,
    'background_color': (0, 0, 0),
    'text_color': (255, 255, 255),
}

# 统计配置
STATISTICS_CONFIG: Dict[str, Any] = {
    'sample_size': 1000,  # 统计样本大小
    'confidence_level': 0.95,  # 置信度
}

# 分析配置
ANALYSIS_CONFIG: Dict[str, Any] = {
    'min_battles_for_analysis': 100,  # 最小战斗场次
    'performance_threshold': 0.7,  # 性能阈值
} 