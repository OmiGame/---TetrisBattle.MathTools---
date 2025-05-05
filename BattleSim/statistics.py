"""
战斗统计模块
负责收集和处理战斗过程中的各种数据
"""

from typing import Dict, List, Tuple, Any
from .models.statistics_data import StatisticsData
from .battle_events import (
    PlayerUnitSpawnEvent,
    EnemyUnitSpawnEvent,
    UnitDeathEvent,
    DamageEvent,
    RogueSkillEvent
)

class BattleStatistics:
    def __init__(self):
        """初始化统计模块"""
        # 单位生成统计
        self.player_unit_spawns = 0
        self.enemy_unit_spawns = 0
        self.player_unit_details = []
        self.enemy_unit_details = []
        
        # 单位死亡统计
        self.unit_deaths = {"player": 0, "enemy": 0}
        
        # 伤害统计
        self.damage_dealt = {"player": 0.0, "enemy": 0.0}
        self.damage_taken = {"player": 0.0, "enemy": 0.0}
        
        # 肉鸽技能统计
        self.rogue_skill_count = 0
        self.rogue_skill_details = []
        
        # 时间序列数据
        self.unit_count_time_series = {
            "player": [],  # 存储(timestamp, alive_count)
            "enemy": []
        }
        self.power_time_series = {
            "player": [],  # 存储(timestamp, total_power)
            "enemy": []
        }
        self.damage_time_series = {
            "player_dealt": [],  # 存储(timestamp, damage_dealt)
            "player_taken": [],  # 存储(timestamp, damage_taken)
            "enemy_dealt": [],   # 存储(timestamp, damage_dealt)
            "enemy_taken": []    # 存储(timestamp, damage_taken)
        }
        
        # 战斗时间
        self.start_time = 0.0
        self.end_time = 0.0
        self.winner = None
        
        # 事件处理器映射
        self.event_handlers = {
            "player_unit_spawn": self._handle_player_unit_spawn,
            "enemy_unit_spawn": self._handle_enemy_unit_spawn,
            "unit_death": self._handle_unit_death,
            "damage": self._handle_damage,
            "rogue_skill": self._handle_rogue_skill
        }
    
    def start_battle(self):
        """开始战斗统计"""
        self.start_time = 0.0
        self._update_time_series()
    
    def end_battle(self, winner: str):
        """结束战斗统计"""
        self.end_time = 0.0
        self.winner = winner
        self._update_time_series()
    
    def handle_event(self, event: Any):
        """处理战斗事件"""
        event_type = event.event_type
        if event_type in self.event_handlers:
            self.event_handlers[event_type](event)
            self._update_time_series()
    
    def _update_time_series(self):
        """更新时间序列数据"""
        current_time = self.end_time if self.end_time > 0 else self.start_time
        
        # 更新单位数量时间序列
        player_alive = self.player_unit_spawns - self.unit_deaths["player"]
        enemy_alive = self.enemy_unit_spawns - self.unit_deaths["enemy"]
        self.unit_count_time_series["player"].append((current_time, player_alive))
        self.unit_count_time_series["enemy"].append((current_time, enemy_alive))
        
        # 更新战力时间序列
        player_power = sum(unit["attack"] * unit["health"] for unit in self.player_unit_details)
        enemy_power = sum(unit["attack"] * unit["health"] for unit in self.enemy_unit_details)
        self.power_time_series["player"].append((current_time, player_power))
        self.power_time_series["enemy"].append((current_time, enemy_power))
        
        # 更新伤害时间序列
        self.damage_time_series["player_dealt"].append((current_time, self.damage_dealt["player"]))
        self.damage_time_series["player_taken"].append((current_time, self.damage_taken["player"]))
        self.damage_time_series["enemy_dealt"].append((current_time, self.damage_dealt["enemy"]))
        self.damage_time_series["enemy_taken"].append((current_time, self.damage_taken["enemy"]))
    
    def _handle_player_unit_spawn(self, event: PlayerUnitSpawnEvent):
        """处理玩家单位生成事件"""
        self.player_unit_spawns += 1
        self.player_unit_details.append({
            "type": event.unit_type,
            "attack": event.unit_attributes["attack"],
            "health": event.unit_attributes["health"],
            "timestamp": event.timestamp
        })
    
    def _handle_enemy_unit_spawn(self, event: EnemyUnitSpawnEvent):
        """处理敌方单位生成事件"""
        self.enemy_unit_spawns += 1
        self.enemy_unit_details.append({
            "type": event.unit_type,
            "attack": event.unit_attributes["attack"],
            "health": event.unit_attributes["health"],
            "timestamp": event.timestamp
        })
    
    def _handle_unit_death(self, event: UnitDeathEvent):
        """处理单位死亡事件"""
        self.unit_deaths[event.unit_side] += 1
    
    def _handle_damage(self, event: DamageEvent):
        """处理伤害事件"""
        self.damage_dealt[event.attacker_side] += event.damage_amount
        self.damage_taken[event.target_side] += event.damage_amount
    
    def _handle_rogue_skill(self, event: RogueSkillEvent):
        """处理肉鸽技能事件"""
        self.rogue_skill_count += 1
        self.rogue_skill_details.append({
            "skill_type": event.skill_type,
            "affected_units": event.affected_units,
            "skill_attributes": event.skill_attributes,
            "timestamp": event.timestamp
        })
    
    def calculate_statistics(self) -> StatisticsData:
        """计算并返回完整的统计数据"""
        return StatisticsData(
            battle_duration=self.end_time - self.start_time,
            total_battles=1,  # 当前只统计单场战斗
            win_rate=1.0 if self.winner == "player" else 0.0,  # 当前只统计单场战斗
            average_turns=0.0,  # 当前未实现回合统计
            damage_distribution={
                "player": [self.damage_dealt["player"]],
                "enemy": [self.damage_dealt["enemy"]]
            },
            survival_rates={
                "player": (self.player_unit_spawns - self.unit_deaths["player"]) / self.player_unit_spawns if self.player_unit_spawns > 0 else 0.0,
                "enemy": (self.enemy_unit_spawns - self.unit_deaths["enemy"]) / self.enemy_unit_spawns if self.enemy_unit_spawns > 0 else 0.0
            },
            turn_statistics={},  # 当前未实现回合统计
            battle_results=[{
                "winner": self.winner,
                "duration": self.end_time - self.start_time,
                "player_units": self.player_unit_spawns,
                "enemy_units": self.enemy_unit_spawns,
                "player_deaths": self.unit_deaths["player"],
                "enemy_deaths": self.unit_deaths["enemy"],
                "player_damage": self.damage_dealt["player"],
                "enemy_damage": self.damage_dealt["enemy"]
            }],
            player_unit_spawns=self.player_unit_spawns,
            enemy_unit_spawns=self.enemy_unit_spawns,
            player_unit_details=self.player_unit_details,
            enemy_unit_details=self.enemy_unit_details,
            unit_deaths=self.unit_deaths,
            damage_dealt=self.damage_dealt,
            damage_taken=self.damage_taken,
            rogue_skill_count=self.rogue_skill_count,
            rogue_skill_details=self.rogue_skill_details,
            unit_count_time_series=self.unit_count_time_series,
            power_time_series=self.power_time_series,
            damage_time_series=self.damage_time_series
        )
    
    def calculate_battle_stats(self) -> Dict[str, any]:
        """计算当前战斗状态的信息"""
        player_alive = self.player_unit_spawns - self.unit_deaths["player"]
        enemy_alive = self.enemy_unit_spawns - self.unit_deaths["enemy"]
        
        # 计算总战力
        player_power = sum(unit["attack"] * unit["health"] for unit in self.player_unit_details)
        enemy_power = sum(unit["attack"] * unit["health"] for unit in self.enemy_unit_details)
        
        return {
            "player": {
                "alive_units": player_alive,
                "total_power": player_power
            },
            "enemy": {
                "alive_units": enemy_alive,
                "total_power": enemy_power
            },
            "rogue_skill_count": self.rogue_skill_count
        }
    
   
    
  