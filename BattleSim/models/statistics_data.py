"""
统计数据模型
"""

from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class StatisticsData:
    """统计数据类"""
    battle_duration: float
    total_battles: int
    win_rate: float
    average_turns: float
    damage_distribution: Dict[str, List[float]]
    survival_rates: Dict[str, float]
    turn_statistics: Dict[str, Any]
    battle_results: List[Dict[str, Any]]
    
    # 单位生成统计
    player_unit_spawns: int
    enemy_unit_spawns: int
    player_unit_details: List[Dict[str, Any]]
    enemy_unit_details: List[Dict[str, Any]]
    
    # 单位死亡统计
    unit_deaths: Dict[str, int]
    
    # 伤害统计
    damage_dealt: Dict[str, float]
    damage_taken: Dict[str, float]
    
    # 肉鸽技能统计
    rogue_skill_count: int
    rogue_skill_details: List[Dict[str, Any]]
    
    # 时间序列数据
    unit_count_time_series: Dict[str, List[tuple]]
    power_time_series: Dict[str, List[tuple]]
    damage_time_series: Dict[str, List[tuple]]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'battle_duration': self.battle_duration,
            'total_battles': self.total_battles,
            'win_rate': self.win_rate,
            'average_turns': self.average_turns,
            'damage_distribution': self.damage_distribution,
            'survival_rates': self.survival_rates,
            'turn_statistics': self.turn_statistics,
            'battle_results': self.battle_results,
            'player_unit_spawns': self.player_unit_spawns,
            'enemy_unit_spawns': self.enemy_unit_spawns,
            'player_unit_details': self.player_unit_details,
            'enemy_unit_details': self.enemy_unit_details,
            'unit_deaths': self.unit_deaths,
            'damage_dealt': self.damage_dealt,
            'damage_taken': self.damage_taken,
            'rogue_skill_count': self.rogue_skill_count,
            'rogue_skill_details': self.rogue_skill_details,
            'unit_count_time_series': self.unit_count_time_series,
            'power_time_series': self.power_time_series,
            'damage_time_series': self.damage_time_series
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatisticsData':
        """从字典创建实例"""
        return cls(
            battle_duration=data['battle_duration'],
            total_battles=data['total_battles'],
            win_rate=data['win_rate'],
            average_turns=data['average_turns'],
            damage_distribution=data['damage_distribution'],
            survival_rates=data['survival_rates'],
            turn_statistics=data['turn_statistics'],
            battle_results=data['battle_results'],
            player_unit_spawns=data['player_unit_spawns'],
            enemy_unit_spawns=data['enemy_unit_spawns'],
            player_unit_details=data['player_unit_details'],
            enemy_unit_details=data['enemy_unit_details'],
            unit_deaths=data['unit_deaths'],
            damage_dealt=data['damage_dealt'],
            damage_taken=data['damage_taken'],
            rogue_skill_count=data['rogue_skill_count'],
            rogue_skill_details=data['rogue_skill_details'],
            unit_count_time_series=data['unit_count_time_series'],
            power_time_series=data['power_time_series'],
            damage_time_series=data['damage_time_series']
        ) 