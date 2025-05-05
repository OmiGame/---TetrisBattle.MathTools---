"""
战斗结果数据模型
"""

from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class BattleResult:
    """战斗结果数据类，记录单场战斗的基本结果"""
    winner: str  # 胜利方
    total_duration: float  # 总战斗时长（秒）
    player_tower_hp: float  # 玩家防御塔最终血量
    enemy_tower_hp: float  # 敌方防御塔最终血量
    player_units_alive: int  # 存活的玩家单位数量
    enemy_units_alive: int  # 存活的敌方单位数量
    battle_log: List[str]  # 战斗日志
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'winner': self.winner,
            'total_duration': self.total_duration,
            'player_tower_hp': self.player_tower_hp,
            'enemy_tower_hp': self.enemy_tower_hp,
            'player_units_alive': self.player_units_alive,
            'enemy_units_alive': self.enemy_units_alive,
            'battle_log': self.battle_log
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BattleResult':
        """从字典创建实例"""
        return cls(
            winner=data['winner'],
            total_duration=data['total_duration'],
            player_tower_hp=data['player_tower_hp'],
            enemy_tower_hp=data['enemy_tower_hp'],
            player_units_alive=data['player_units_alive'],
            enemy_units_alive=data['enemy_units_alive'],
            battle_log=data['battle_log']
        ) 