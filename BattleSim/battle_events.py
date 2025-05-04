"""
战斗事件定义模块
定义战斗过程中可能发生的各种事件
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from .models.battle_state import Unit, UnitState

@dataclass
class BattleEvent:
    """战斗事件基类"""
    event_type: str
    timestamp: float
    data: Dict[str, Any]

@dataclass
class PlayerUnitSpawnEvent(BattleEvent):
    """我方单位生成事件"""
    unit: Unit
    unit_attributes: Dict[str, float]  # 记录单位生成时的属性值

@dataclass
class EnemyUnitSpawnEvent(BattleEvent):
    """敌方单位生成事件"""
    unit: Unit
    unit_attributes: Dict[str, float]  # 记录单位生成时的属性值

@dataclass
class UnitDeathEvent(BattleEvent):
    """单位死亡事件"""
    unit: Unit
    killer_id: Optional[str]  # 击杀者ID

@dataclass
class DamageEvent(BattleEvent):
    """伤害事件"""
    attacker: Unit
    target: Unit
    damage: float

@dataclass
class RogueSkillEvent(BattleEvent):
    """肉鸽技能事件"""
    skill_name: str
    affected_units: List[Unit]
    skill_attributes: Dict[str, float]  # 记录技能属性

@dataclass
class BattleEndEvent(BattleEvent):
    """战斗结束事件"""
    winner: str
    duration: float

# 事件类型常量
EVENT_PLAYER_UNIT_SPAWN = "player_unit_spawn"
EVENT_ENEMY_UNIT_SPAWN = "enemy_unit_spawn"
EVENT_UNIT_DEATH = "unit_death"
EVENT_DAMAGE = "damage"
EVENT_ROGUE_SKILL = "rogue_skill"
EVENT_BATTLE_END = "battle_end" 