"""
战斗配置文件
"""

from typing import Dict, Any, List
from BattleSim.models.battle_state import Position, WaveConfig, PlayerConfig
import path_config  # 导入路径配置

# 波次配置
WAVE_CONFIGS: List[WaveConfig] = [
    WaveConfig(
        wave_id=1,
        unit_type="普通敌人",
        unit_count=10,
        unit_level=1,
        spawn_interval=2.0,
        spawn_position=Position(x=40, y=0),
        unit_config={
            "hp": 100,
            "attack": 10,
            "attack_speed": 1.0,
            "attack_range": 2.0,
            "move_speed": 1.0,
            "tower_damage": 1
        }
    ),
    WaveConfig(
        wave_id=2,
        unit_type="精英敌人",
        unit_count=5,
        unit_level=2,
        spawn_interval=3.0,
        spawn_position=Position(x=40, y=0),
        unit_config={
            "hp": 200,
            "attack": 20,
            "attack_speed": 1.2,
            "attack_range": 2.5,
            "move_speed": 1.2,
            "tower_damage": 1
        }
    )
]

# 玩家配置
PLAYER_CONFIG = PlayerConfig(
    units=[
        {
            "level": 1,
            "hp": 100,
            "attack": 15,
            "attack_speed": 1.2,
            "attack_range": 2.5,
            "move_speed": 1.2,
            "tower_damage": 1
        },
        {
            "level": 1,
            "hp": 80,
            "attack": 20,
            "attack_speed": 1.5,
            "attack_range": 2.0,
            "move_speed": 1.5,
            "tower_damage": 1
        },
        {
            "level": 1,
            "hp": 120,
            "attack": 10,
            "attack_speed": 1.0,
            "attack_range": 3.0,
            "move_speed": 1.0,
            "tower_damage": 1
        }
    ],
    spawn_interval={"min": 1.0, "max": 2.0},
    spawn_position=Position(x=0, y=0),
    spawn_range=10.0
)

# 防御塔配置
TOWER_CONFIG = {
    "player_tower": {
        "hp": 1000,
        "attack": 0,
        "attack_speed": 0,
        "attack_range": 0,
        "move_speed": 0,
        "position": Position(x=0, y=300),  # 左侧中间
        "tower_damage" : 0
    },
    "enemy_tower": {
        "hp": 1000,
        "attack": 0,
        "attack_speed": 0,
        "attack_range": 0,
        "move_speed": 0,
        "position": Position(x=40, y=300),  # 右侧中间
        "tower_damage" : 0
    }
}

# 肉鸽技能配置
ROGUE_SKILLS = {
    "permanent_boost": {
        "name": "永久强化",
        "hp_multiplier": 1.5,
        "attack_multiplier": 1.5,
        "attack_speed_multiplier": 1.2,
        "spawn_speed_multiplier": 1.0,
        "duration": 0,  # 这个值会被忽略
        "is_permanent": True
    },
    "temporary_boost": {
        "name": "临时强化",
        "hp_multiplier": 2.0,
        "attack_multiplier": 2.0,
        "attack_speed_multiplier": 1.5,
        "spawn_speed_multiplier": 1.0,
        "duration": 10.0,
        "is_permanent": True
    },
    "speed_boost": {
        "name": "速度提升",
        "hp_multiplier": 1.0,
        "attack_multiplier": 1.0,
        "attack_speed_multiplier": 2.0,
        "spawn_speed_multiplier": 1.5,
        "duration": 15.0,
        "is_permanent": True
    }
}

# 平均强度肉鸽技能
AVERAGE_ROGUE_SKILL = {
    "name": "均衡强化",
    "hp_multiplier": 1.2,
    "attack_multiplier": 1.2,
    "attack_speed_multiplier": 1.2,
    "spawn_speed_multiplier": 1.5,
    "duration": 10.0,
    "is_permanent": True
}

# 肉鸽技能触发配置
ROGUE_SKILL_TRIGGER = {
    "use_timeline": True,  # 是否使用时间轴触发
    "timeline": [5.0, 15.0, 25.0],  # 触发时间点（秒）
    "random_trigger": False,  # 是否随机时间触发
    "min_interval": 10.0,  # 最小触发间隔（秒）
    "max_interval": 20.0   # 最大触发间隔（秒）
} 