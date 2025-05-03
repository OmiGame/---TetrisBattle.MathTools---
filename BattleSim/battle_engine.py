"""
战斗引擎模块
负责实现战斗过程的核心逻辑
"""

import random
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from .models.battle_state import (
    BattleState, Unit, UnitType, UnitState, Position, WaveConfig, PlayerConfig, RogueSkill
)
from .models.battle_result import BattleResult
from .battle_configs.battle_config import  ROGUE_SKILLS, AVERAGE_ROGUE_SKILL, ROGUE_SKILL_TRIGGER
from .global_config import BATTLE_ENGINE_CONFIG
from .utils import set_random_seed, format_battle_log

class BattleEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化战斗引擎"""
        self.config = config or BATTLE_ENGINE_CONFIG
        set_random_seed(self.config.get('random_seed'))
        self.last_update_time = time.time()
        self.unit_id_counter = 0
        self.keyboard_spawn_cooldown = 0.5   # 键盘生成冷却时间（秒）
    
    def _generate_unit_id(self, unit_type: str) -> str:
        """生成唯一的单位ID"""
        self.unit_id_counter += 1
        return f"{unit_type}_{self.unit_id_counter}_{uuid.uuid4().hex[:8]}"
    
    def initialize_battle(
        self,
        player_config: PlayerConfig,
        wave_configs: List[WaveConfig],
        player_tower: Optional[Unit] = None,
        enemy_tower: Optional[Unit] = None
    ) -> BattleState:
        """初始化战斗状态"""
        # 生成随机的单位生成顺序
        unit_count = len(player_config.units)
        spawn_order = list(range(unit_count))
        random.shuffle(spawn_order)
        
        # 设置肉鸽技能时间轴
        rogue_skill_timeline = []
        if ROGUE_SKILL_TRIGGER["use_timeline"]:
            rogue_skill_timeline = ROGUE_SKILL_TRIGGER["timeline"].copy()
        
        return BattleState(
            start_time=time.time(),
            player_units=[],
            enemy_units=[],
            player_tower=player_tower,
            enemy_tower=enemy_tower,
            active_effects=[],
            battle_log=[],
            current_wave=0,
            wave_configs=wave_configs,
            player_config=player_config,
            last_spawn_time={},
            last_enhance_time=0.0,
            units_spawned_since_enhance=0,
            game_over=False,
            winner=None,
            current_unit_index=0,
            unit_spawn_order=spawn_order,
            rogue_skill_timeline=rogue_skill_timeline,
            next_rogue_skill_time=rogue_skill_timeline[0] if rogue_skill_timeline else 0.0,
            active_rogue_skills={},
            keyboard_spawn_cooldown=0.5
        )
    
    def run_battle(self, battle_state: BattleState) -> BattleResult:
        """执行战斗过程"""
        while not battle_state.game_over:
            self._update_battle(battle_state)
            
            # 检查是否超时
            if time.time() - battle_state.start_time >= self.config['max_battle_time']:
                battle_state.game_over = True
                battle_state.winner = "draw"
        
        return self._generate_battle_result(battle_state)
    
    def _update_battle(self, battle_state: BattleState) -> None:
        """更新战斗状态"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 更新键盘生成冷却
        if battle_state.keyboard_spawn_cooldown > 0:
            battle_state.keyboard_spawn_cooldown = max(0, battle_state.keyboard_spawn_cooldown - delta_time)
        
        # 检查肉鸽技能触发
        self._check_rogue_skill_trigger(battle_state, current_time)
        
        # 更新肉鸽技能状态
        self._update_rogue_skills(battle_state, current_time)
        
        # 生成单位
        self._spawn_units(battle_state, delta_time)
        
        # 更新单位状态
        self._update_units(battle_state, delta_time)
        
        # 检查战斗结束条件
        self._check_battle_end(battle_state)
    
    def _check_rogue_skill_trigger(self, battle_state: BattleState, current_time: float) -> None:
        """检查肉鸽技能触发条件"""
        battle_duration = current_time - battle_state.start_time
        
        if ROGUE_SKILL_TRIGGER["use_timeline"]:
            # 时间轴触发
            if battle_state.rogue_skill_timeline and battle_duration >= battle_state.rogue_skill_timeline[0]:
                self._trigger_rogue_skill(battle_state)
                battle_state.rogue_skill_timeline.pop(0)
                if battle_state.rogue_skill_timeline:
                    battle_state.next_rogue_skill_time = battle_state.rogue_skill_timeline[0]
        elif ROGUE_SKILL_TRIGGER["random_trigger"]:
            # 随机触发
            if battle_duration >= battle_state.next_rogue_skill_time:
                self._trigger_rogue_skill(battle_state)
                interval = random.uniform(
                    ROGUE_SKILL_TRIGGER["min_interval"],
                    ROGUE_SKILL_TRIGGER["max_interval"]
                )
                battle_state.next_rogue_skill_time = battle_duration + interval
    
    def _trigger_rogue_skill(self, battle_state: BattleState) -> None:
        """触发肉鸽技能"""
        # 随机选择一个肉鸽技能
        skill_name = random.choice(list(ROGUE_SKILLS.keys()))
        skill_config = ROGUE_SKILLS[skill_name]
        
        # 创建技能实例
        skill = RogueSkill(
            name=skill_config["name"],
            hp_multiplier=skill_config["hp_multiplier"],
            attack_multiplier=skill_config["attack_multiplier"],
            attack_speed_multiplier=skill_config["attack_speed_multiplier"],
            spawn_speed_multiplier=skill_config["spawn_speed_multiplier"],
            duration=skill_config["duration"],
            is_permanent=skill_config["is_permanent"],
            start_time=time.time()
        )
        
        # 应用技能效果到所有玩家单位
        for unit in battle_state.player_units:
            if unit.state != UnitState.DEAD:
                # 基于初始属性计算强化后的属性
                unit.hp += unit.initial_attrs["hp"] * skill.hp_multiplier
                unit.max_hp += unit.initial_attrs["max_hp"] * skill.hp_multiplier
                unit.attack += unit.initial_attrs["attack"] * skill.attack_multiplier
                unit.attack_speed += unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
                
                # 记录当前技能效果
                unit.buffs[skill_name] = {
                    "multipliers": {
                        "hp": skill.hp_multiplier,
                        "attack": skill.attack_multiplier,
                        "attack_speed": skill.attack_speed_multiplier
                    },
                    "duration": skill.duration,
                    "start_time": skill.start_time
                }
        
        # 应用生成速度倍率
        battle_state.player_config.spawn_interval = {
            "min": battle_state.player_config.spawn_interval["min"] / skill.spawn_speed_multiplier,
            "max": battle_state.player_config.spawn_interval["max"] / skill.spawn_speed_multiplier
        }
        
        battle_state.active_rogue_skills[skill_name] = skill
        battle_state.battle_log.append(f"触发肉鸽技能: {skill.name} (生成速度提升 {skill.spawn_speed_multiplier}倍)")
    
    def handle_keyboard_input(self, battle_state: BattleState, key: str) -> None:
        """处理键盘输入"""
        if key == " " and battle_state.keyboard_spawn_cooldown <= 0:
            self._spawn_player_unit(battle_state)
            battle_state.keyboard_spawn_cooldown = self.keyboard_spawn_cooldown
            battle_state.battle_log.append("通过键盘输入生成玩家单位")
        elif key == "\r":  # 回车键
            # 触发平均肉鸽技能
            self._trigger_average_rogue_skill(battle_state)
            battle_state.battle_log.append("通过键盘输入触发平均肉鸽技能")
    
    def _trigger_average_rogue_skill(self, battle_state: BattleState) -> None:
        """触发平均肉鸽技能"""
        skill_config = AVERAGE_ROGUE_SKILL
        
        # 创建技能实例
        skill = RogueSkill(
            name=skill_config["name"],
            hp_multiplier=skill_config["hp_multiplier"],
            attack_multiplier=skill_config["attack_multiplier"],
            attack_speed_multiplier=skill_config["attack_speed_multiplier"],
            spawn_speed_multiplier=skill_config["spawn_speed_multiplier"],
            duration=skill_config["duration"],
            is_permanent=skill_config["is_permanent"],
            start_time=time.time()
        )
        
        # 应用技能效果到所有玩家单位
        for unit in battle_state.player_units:
            if unit.state != UnitState.DEAD:
                # 基于初始属性计算强化后的属性
                unit.hp += unit.initial_attrs["hp"] * skill.hp_multiplier
                unit.max_hp += unit.initial_attrs["max_hp"] * skill.hp_multiplier
                unit.attack += unit.initial_attrs["attack"] * skill.attack_multiplier
                unit.attack_speed += unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
                
                # 记录当前技能效果
                unit.buffs["average_rogue_skill"] = {
                    "multipliers": {
                        "hp": skill.hp_multiplier,
                        "attack": skill.attack_multiplier,
                        "attack_speed": skill.attack_speed_multiplier
                    },
                    "duration": skill.duration,
                    "start_time": skill.start_time
                }
        
        # 应用生成速度倍率
        battle_state.player_config.spawn_interval = {
            "min": battle_state.player_config.spawn_interval["min"] / skill.spawn_speed_multiplier,
            "max": battle_state.player_config.spawn_interval["max"] / skill.spawn_speed_multiplier
        }
        
        battle_state.active_rogue_skills["average_rogue_skill"] = skill
    
    def _spawn_units(self, battle_state: BattleState, delta_time: float) -> None:
        """生成单位"""
        current_time = time.time()
        
        # 生成敌方单位
        if battle_state.current_wave < len(battle_state.wave_configs):
            wave = battle_state.wave_configs[battle_state.current_wave]
            if wave.unit_count > 0:
                if 'enemy_spawn' not in battle_state.last_spawn_time:
                    battle_state.last_spawn_time['enemy_spawn'] = current_time
                
                if current_time - battle_state.last_spawn_time['enemy_spawn'] >= wave.spawn_interval:
                    self._spawn_enemy_unit(battle_state, wave)
                    wave.unit_count -= 1
                    battle_state.last_spawn_time['enemy_spawn'] = current_time
                    
                    if wave.unit_count == 0:
                        battle_state.current_wave += 1
        
        # 生成玩家单位
        if 'player_spawn' not in battle_state.last_spawn_time:
            battle_state.last_spawn_time['player_spawn'] = current_time
        
        spawn_interval = random.uniform(
            battle_state.player_config.spawn_interval['min'],
            battle_state.player_config.spawn_interval['max']
        )
        
        if current_time - battle_state.last_spawn_time['player_spawn'] >= spawn_interval:
            self._spawn_player_unit(battle_state)
            battle_state.last_spawn_time['player_spawn'] = current_time
            battle_state.units_spawned_since_enhance += 1
    
    def _spawn_enemy_unit(self, battle_state: BattleState, wave: WaveConfig) -> None:
        """生成敌方单位之前，从波次配置中读取单位属性，创建敌方单位实例，添加到敌方单位列表"""
        unit_config = wave.unit_config
        
        unit = Unit(
            id=self._generate_unit_id("enemy"),
            type=UnitType.ENEMY,
            level=wave.unit_level,
            hp=unit_config['hp'],
            max_hp=unit_config['hp'],
            attack=unit_config['attack'],
            attack_speed=unit_config['attack_speed'],
            attack_range=unit_config['attack_range'],
            move_speed=unit_config['move_speed'],
            position=wave.spawn_position
        )
        battle_state.enemy_units.append(unit)
        battle_state.battle_log.append(f"敌方单位 {unit.id} 已生成")
    
    def _spawn_player_unit(self, battle_state: BattleState) -> None:
        """生成玩家单位"""
        # 获取当前要生成的单位索引
        unit_index = battle_state.unit_spawn_order[battle_state.current_unit_index]
        unit_config = battle_state.player_config.units[unit_index]
        
        # 更新索引，循环遍历
        battle_state.current_unit_index = (battle_state.current_unit_index + 1) % len(battle_state.player_config.units)
        
        # 在生成范围内随机位置
        spawn_x = battle_state.player_config.spawn_position.x + random.uniform(
            -battle_state.player_config.spawn_range,
            battle_state.player_config.spawn_range
        )
        spawn_y = battle_state.player_config.spawn_position.y
        
        # 记录初始属性
        initial_attrs = {
            "hp": unit_config['hp'],
            "max_hp": unit_config['hp'],
            "attack": unit_config['attack'],
            "attack_speed": unit_config['attack_speed']
        }
        
        unit = Unit(
            id=self._generate_unit_id("player"),
            type=UnitType.PLAYER,
            level=unit_config['level'],
            hp=unit_config['hp'],
            max_hp=unit_config['hp'],
            attack=unit_config['attack'],
            attack_speed=unit_config['attack_speed'],
            attack_range=unit_config['attack_range'],
            move_speed=unit_config['move_speed'],
            position=Position(spawn_x, spawn_y),
            initial_attrs=initial_attrs  # 记录初始属性
        )
        battle_state.player_units.append(unit)
        battle_state.battle_log.append(f"玩家单位 {unit.id} 已生成")
    
    def _update_units(self, battle_state: BattleState, delta_time: float) -> None:
        """更新单位状态"""
        current_time = time.time()
        
        # 更新玩家单位
        for unit in battle_state.player_units:
            if unit.state == UnitState.DEAD:
                continue
            
            # 检查buff持续时间
            expired_buffs = []
            for skill_name, buff in unit.buffs.items():
                if current_time - buff["start_time"] >= buff["duration"]:
                    # 恢复初始属性
                    unit.hp = unit.initial_attrs["hp"]
                    unit.max_hp = unit.initial_attrs["max_hp"]
                    unit.attack = unit.initial_attrs["attack"]
                    unit.attack_speed = unit.initial_attrs["attack_speed"]
                    expired_buffs.append(skill_name)
            
            for skill_name in expired_buffs:
                del unit.buffs[skill_name]
                # 恢复生成速度
                if skill_name in battle_state.active_rogue_skills:
                    skill = battle_state.active_rogue_skills[skill_name]
                    battle_state.player_config.spawn_interval = {
                        "min": battle_state.player_config.spawn_interval["min"] * skill.spawn_speed_multiplier,
                        "max": battle_state.player_config.spawn_interval["max"] * skill.spawn_speed_multiplier
                    }
                    del battle_state.active_rogue_skills[skill_name]
            
            # 更新单位行为
            self._update_unit_behavior(unit, battle_state, delta_time)
        
        # 更新敌方单位
        for unit in battle_state.enemy_units:
            if unit.state == UnitState.DEAD:
                continue
            self._update_unit_behavior(unit, battle_state, delta_time)
    
    def _update_unit_behavior(self, unit: Unit, battle_state: BattleState, delta_time: float) -> None:
        """更新单位行为"""
        # 寻找目标
        if not unit.target_id or unit.state == UnitState.IDLE:
            self._find_target(unit, battle_state)
        
        # 移动或攻击
        if unit.target_id:
            target = self._get_unit_by_id(unit.target_id, battle_state)
            if target:
                distance = self._calculate_distance(unit.position, target.position)
                if distance <= unit.attack_range:
                    self._attack_target(unit, target, battle_state)
                else:
                    self._move_towards_target(unit, target, delta_time)
            else:
                unit.target_id = None
                unit.state = UnitState.IDLE
    
    def _find_target(self, unit: Unit, battle_state: BattleState) -> None:
        """寻找目标"""
        if unit.type == UnitType.PLAYER:
            potential_targets = battle_state.enemy_units
        else:
            potential_targets = battle_state.player_units
        
        # 找到最近的目标
        closest_target = None
        min_distance = float('inf')
        
        for target in potential_targets:
            if target.state != UnitState.DEAD:
                distance = self._calculate_distance(unit.position, target.position)
                if distance < min_distance:
                    min_distance = distance
                    closest_target = target
        
        if closest_target:
            unit.target_id = closest_target.id
            unit.state = UnitState.MOVING
    
    def _attack_target(self, unit: Unit, target: Unit, battle_state: BattleState) -> None:
        """攻击目标"""
        unit.state = UnitState.ATTACKING
        damage = unit.attack  # 使用战斗公式计算伤害
        target.hp -= damage
        
        battle_state.battle_log.append(
            f"{unit.id} 对 {target.id} 造成 {damage} 点伤害"
        )
        
        if target.hp <= 0:
            target.state = UnitState.DEAD
            battle_state.battle_log.append(f"{target.id} 已死亡")
            unit.target_id = None
            unit.state = UnitState.IDLE
    
    def _move_towards_target(self, unit: Unit, target: Unit, delta_time: float) -> None:
        """向目标移动"""
        unit.state = UnitState.MOVING
        direction_x = target.position.x - unit.position.x
        direction_y = target.position.y - unit.position.y
        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
        
        if distance > 0:
            move_x = (direction_x / distance) * unit.move_speed * delta_time
            move_y = (direction_y / distance) * unit.move_speed * delta_time
            unit.position.x += move_x
            unit.position.y += move_y
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """计算两点之间的距离"""
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    
    def _get_unit_by_id(self, unit_id: str, battle_state: BattleState) -> Optional[Unit]:
        """根据ID获取单位"""
        for unit in battle_state.player_units + battle_state.enemy_units:
            if unit.id == unit_id:
                return unit
        return None
    
    def _check_battle_end(self, battle_state: BattleState) -> None:
        """检查战斗是否结束"""
        # 检查防御塔
        if battle_state.player_tower and battle_state.player_tower.hp <= 0:
            battle_state.game_over = True
            battle_state.winner = "enemy"
            return
        
        if battle_state.enemy_tower and battle_state.enemy_tower.hp <= 0:
            battle_state.game_over = True
            battle_state.winner = "player"
            return
        
        # 检查单位
        if not battle_state.player_units and not battle_state.enemy_units:
            battle_state.game_over = True
            battle_state.winner = "draw"
            return
    
    def _generate_battle_result(self, battle_state: BattleState) -> BattleResult:
        """生成战斗结果"""
        return BattleResult(
            winner=battle_state.winner,
            total_duration=time.time() - battle_state.start_time,
            player_final_state={
                'units': [unit.__dict__ for unit in battle_state.player_units],
                'tower': battle_state.player_tower.__dict__ if battle_state.player_tower else None
            },
            enemy_final_state={
                'units': [unit.__dict__ for unit in battle_state.enemy_units],
                'tower': battle_state.enemy_tower.__dict__ if battle_state.enemy_tower else None
            },
            damage_dealt={},  # 需要在实际战斗中统计
            damage_taken={},  # 需要在实际战斗中统计
            battle_log=battle_state.battle_log
        )
    
    def enhance_unit(self, unit: Unit, battle_state: BattleState) -> None:
        """强化单位"""
        # 使用战斗公式计算强化后的属性
        enhanced_attributes = self._calculate_enhancement(unit)
        
        # 更新单位属性
        for attr, value in enhanced_attributes.items():
            setattr(unit, attr, value)
        
        battle_state.battle_log.append(f"{unit.id} 已强化")
    
    def _calculate_enhancement(self, unit: Unit) -> Dict[str, float]:
        """计算强化后的属性"""
        # 这里需要调用战斗公式模块
        return {
            'attack': unit.attack * 1.2,
            'hp': unit.hp * 1.2,
            'max_hp': unit.max_hp * 1.2
        }

    def _update_rogue_skills(self, battle_state: BattleState, current_time: float) -> None:
        """更新肉鸽技能状态"""
        # 检查是否有技能过期
        expired_skills = []
        for skill_name, skill in battle_state.active_rogue_skills.items():
            if not skill.is_permanent and skill.is_expired(current_time):
                expired_skills.append(skill_name)
                # 移除技能效果
                for unit in battle_state.player_units:
                    if unit.state != UnitState.DEAD:
                        unit.hp -= unit.initial_attrs["hp"] * skill.hp_multiplier
                        unit.max_hp -= unit.initial_attrs["max_hp"] * skill.hp_multiplier
                        unit.attack -= unit.initial_attrs["attack"] * skill.attack_multiplier
                        unit.attack_speed -= unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
                battle_state.battle_log.append(f"肉鸽技能 {skill.name} 已过期")

        # 移除过期的技能
        for skill_name in expired_skills:
            del battle_state.active_rogue_skills[skill_name] 