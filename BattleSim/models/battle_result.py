"""
战斗结果数据模型
"""

from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class BattleResult:
    """战斗结果数据类"""
    winner: str
    total_duration: float  # 总战斗时长（秒）
    player_final_state: Dict[str, Any]
    enemy_final_state: Dict[str, Any]
    damage_dealt: Dict[str, float]
    damage_taken: Dict[str, float]
    battle_log: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'winner': self.winner,
            'total_duration': self.total_duration,
            'player_final_state': self.player_final_state,
            'enemy_final_state': self.enemy_final_state,
            'damage_dealt': self.damage_dealt,
            'damage_taken': self.damage_taken,
            'battle_log': self.battle_log
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BattleResult':
        """从字典创建实例"""
        return cls(
            winner=data['winner'],
            total_duration=data['total_duration'],
            player_final_state=data['player_final_state'],
            enemy_final_state=data['enemy_final_state'],
            damage_dealt=data['damage_dealt'],
            damage_taken=data['damage_taken'],
            battle_log=data['battle_log']
        ) 