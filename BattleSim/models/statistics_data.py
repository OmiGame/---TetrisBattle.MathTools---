"""
统计数据模型
"""

from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class StatisticsData:
    """统计数据类"""
    total_battles: int
    win_rate: float
    average_turns: float
    damage_distribution: Dict[str, List[float]]
    survival_rates: Dict[str, float]
    turn_statistics: Dict[str, Any]
    battle_results: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'total_battles': self.total_battles,
            'win_rate': self.win_rate,
            'average_turns': self.average_turns,
            'damage_distribution': self.damage_distribution,
            'survival_rates': self.survival_rates,
            'turn_statistics': self.turn_statistics,
            'battle_results': self.battle_results
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatisticsData':
        """从字典创建实例"""
        return cls(
            total_battles=data['total_battles'],
            win_rate=data['win_rate'],
            average_turns=data['average_turns'],
            damage_distribution=data['damage_distribution'],
            survival_rates=data['survival_rates'],
            turn_statistics=data['turn_statistics'],
            battle_results=data['battle_results']
        ) 