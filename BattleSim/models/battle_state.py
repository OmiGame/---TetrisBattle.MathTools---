"""
战斗状态数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import time

class UnitType(Enum):
    """单位类型"""
    PLAYER = "player"
    ENEMY = "enemy"
    TOWER = "tower"

class UnitState(Enum):
    """单位状态"""
    IDLE = "idle"
    MOVING = "moving"
    ATTACKING = "attacking"
    DEAD = "dead"

@dataclass
class Position:
    """位置信息"""
    x: float
    y: float

@dataclass(frozen=True)
class FrozenPosition:
    """不可变的位置信息，用于保存固定坐标"""
    x: float
    y: float

@dataclass
class Unit:
    """单位数据"""
    id: str
    type: UnitType
    level: int
    hp: float
    max_hp: float
    attack: float
    attack_speed: float
    attack_range: float
    move_speed: float
    tower_damage: int
    position: Position              #这里代表的是   游戏坐标系中的position，即中心点在游戏窗口中间的坐标系。
    target_id: Optional[str] = None
    state: UnitState = UnitState.IDLE
    effects: List[Dict[str, Any]] = field(default_factory=list)
    buffs: Dict[str, Dict] = field(default_factory=dict)
    initial_attrs: Dict[str, float] = field(default_factory=dict)  # 初始属性
    last_attack_time: float = field(default=0.0)  # 上次攻击时间

@dataclass
class WaveConfig:
    """波次配置"""
    wave_id: int
    unit_type: str
    unit_count: int
    unit_level: int
    unit_config: Dict
    spawn_interval: float  # 生成间隔（秒）
    spawn_position: FrozenPosition  # 使用FrozenPosition类型
    _initialized: bool = False  # 添加初始化标志


@dataclass
class PlayerConfig:
    """玩家配置"""
    units: List[Dict[str, Any]]  # 角色阵容配置
    spawn_interval: Dict[str, float]  # 生成间隔范围 {"min": 1.0, "max": 2.0}
    spawn_position: Position
    spawn_range: float  # 生成范围

@dataclass
class RogueSkill:
    """肉鸽技能数据类"""
    name: str
    hp_multiplier: float
    attack_multiplier: float
    attack_speed_multiplier: float
    spawn_speed_multiplier: float
    duration: float
    is_permanent: bool = True
    is_repeatable: bool = False  # 是否可重复选择
    start_time: float = field(default=0.0)  # 将在技能触发时设置

    def is_expired(self, current_time: float) -> bool:
        """检查技能是否过期"""
        if self.is_permanent:
            return False
        return current_time - self.start_time >= self.duration

@dataclass
class BattleState:
    """战斗状态数据类"""
    player_units: List[Unit]
    enemy_units: List[Unit]
    player_tower: Optional[Unit]
    enemy_tower: Optional[Unit]
    active_effects: List[Dict[str, Any]]
    battle_log: List[str]
    current_wave: int
    wave_configs: List[WaveConfig]
    player_config: PlayerConfig
    start_time: float = field(default_factory=time.time)
    last_spawn_time: Dict[str, float] = field(default_factory=dict)
    last_enhance_time: float = 0.0
    units_spawned_since_enhance: int = 0
    game_over: bool = False
    winner: Optional[str] = None
    current_unit_index: int = 0  # 当前要生成的玩家单位索引
    unit_spawn_order: List[int] = field(default_factory=list)  # 单位生成顺序
    rogue_skill_timeline: List[float] = field(default_factory=list)
    next_rogue_skill_time: float = 0.0
    active_single_skills: Dict[str, RogueSkill] = field(default_factory=dict)  # 不可重复的技能
    active_repeat_skills: Dict[str, List[RogueSkill]] = field(default_factory=dict)  # 可重复的技能
    keyboard_spawn_cooldown: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'start_time': self.start_time,
            'player_units': [unit.__dict__ for unit in self.player_units],
            'enemy_units': [unit.__dict__ for unit in self.enemy_units],
            'player_tower': self.player_tower.__dict__ if self.player_tower else None,
            'enemy_tower': self.enemy_tower.__dict__ if self.enemy_tower else None,
            'active_effects': self.active_effects,
            'battle_log': self.battle_log,
            'current_wave': self.current_wave,
            'wave_configs': [wave.__dict__ for wave in self.wave_configs],
            'player_config': self.player_config.__dict__,
            'last_spawn_time': self.last_spawn_time,
            'last_enhance_time': self.last_enhance_time,
            'units_spawned_since_enhance': self.units_spawned_since_enhance,
            'game_over': self.game_over,
            'winner': self.winner,
            'current_unit_index': self.current_unit_index,
            'unit_spawn_order': self.unit_spawn_order,
            'rogue_skill_timeline': self.rogue_skill_timeline,
            'next_rogue_skill_time': self.next_rogue_skill_time,
            'active_single_skills': self.active_single_skills,
            'active_repeat_skills': self.active_repeat_skills,
            'keyboard_spawn_cooldown': self.keyboard_spawn_cooldown
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BattleState':
        """从字典创建实例"""
        return cls(
            player_units=[Unit(**unit_data) for unit_data in data['player_units']],
            enemy_units=[Unit(**unit_data) for unit_data in data['enemy_units']],
            player_tower=Unit(**data['player_tower']) if data['player_tower'] else None,
            enemy_tower=Unit(**data['enemy_tower']) if data['enemy_tower'] else None,
            active_effects=data['active_effects'],
            battle_log=data['battle_log'],
            current_wave=data['current_wave'],
            wave_configs=[WaveConfig(**wave_data) for wave_data in data['wave_configs']],
            player_config=PlayerConfig(**data['player_config']),
            start_time=data['start_time'],
            last_spawn_time=data['last_spawn_time'],
            last_enhance_time=data['last_enhance_time'],
            units_spawned_since_enhance=data['units_spawned_since_enhance'],
            game_over=data['game_over'],
            winner=data['winner'],
            current_unit_index=data['current_unit_index'],
            unit_spawn_order=data['unit_spawn_order'],
            rogue_skill_timeline=data['rogue_skill_timeline'],
            next_rogue_skill_time=data['next_rogue_skill_time'],
            active_single_skills=data['active_single_skills'],
            active_repeat_skills=data['active_repeat_skills'],
            keyboard_spawn_cooldown=data['keyboard_spawn_cooldown']
        ) 