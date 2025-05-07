"""
战斗引擎模块
负责实现战斗过程的核心逻辑
"""

import random
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Callable
from .models.battle_state import (
    BattleState, Unit, UnitType, UnitState, Position, WaveConfig, PlayerConfig, RogueSkill
)
from .models.battle_result import BattleResult
from .battle_configs.battle_config import  ROGUE_SKILLS, AVERAGE_ROGUE_SKILL, ROGUE_SKILL_TRIGGER
from .global_config import BATTLE_ENGINE_CONFIG
from .utils import set_random_seed, format_battle_log, logger
from .battle_events import (
    BattleEvent, PlayerUnitSpawnEvent, EnemyUnitSpawnEvent, UnitDeathEvent,
    DamageEvent, RogueSkillEvent, BattleEndEvent
)
from .statistics import BattleStatistics
from .data_export import BattleDataExporter
from BattleSim.models import battle_state

class BattleEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化战斗引擎"""
        self.config = config or BATTLE_ENGINE_CONFIG
        set_random_seed(self.config.get('random_seed'))
        self.last_update_time = time.time()
        self.unit_id_counter = 0
        self.keyboard_spawn_cooldown = 0.5   # 键盘生成冷却时间（秒）
        self.event_handlers: List[Callable] = []
        self.statistics = BattleStatistics()
        self.data_exporter = BattleDataExporter()
        self.battle_state = None  # 初始化为None，等待initialize_battle时创建
    
    def register_event_handler(self, handler: Callable) -> None:
        """注册事件处理器"""
        self.event_handlers.append(handler)
    
    def _emit_event(self, event: BattleEvent) -> None:
        """触发事件"""
        for handler in self.event_handlers:
            handler(event)
    
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
        
        # 创建新的战斗状态
        self.battle_state = BattleState(
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
            active_single_skills={},  # 使用新的技能存储结构
            active_repeat_skills={},  # 使用新的技能存储结构
            keyboard_spawn_cooldown=0.5
        )
        
        return self.battle_state
    
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
        
        # 输出当前战斗状态
        logger.log_battle_state(battle_state)
        
        # 更新键盘生成冷却
        if battle_state.keyboard_spawn_cooldown > 0:
            battle_state.keyboard_spawn_cooldown = max(0, battle_state.keyboard_spawn_cooldown - delta_time)
        
        # 检查肉鸽技能触发
        self._check_rogue_skill_trigger(battle_state, current_time)
        
        # 更新肉鸽技能状态
        self._update_rogue_skills(battle_state, current_time)
        
        # 生成单位
        self._spawn_units(battle_state, delta_time)
        
        # 更新单位状态（包括肉鸽技能buff效果）
        self._update_units(battle_state, delta_time)
        
        # 检查战斗结束条件
        self._check_battle_end(battle_state)
        
        # 输出战斗日志
        logger.log_battle_log(battle_state.battle_log)
    
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
            is_repeatable=skill_config.get("is_repeatable", False),
            start_time=time.time()
        )
        
        # 应用技能效果到所有玩家单位
        affected_units = []
        for unit in battle_state.player_units:
            if unit.state != UnitState.DEAD:
                # 基于初始属性计算强化后的属性
                unit.hp += unit.initial_attrs["hp"] * skill.hp_multiplier
                unit.max_hp += unit.initial_attrs["max_hp"] * skill.hp_multiplier
                unit.attack += unit.initial_attrs["attack"] * skill.attack_multiplier
                unit.attack_speed += unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
                affected_units.append(unit)
        
        # 应用生成速度倍率    
        battle_state.player_config.spawn_interval = {
            "min": battle_state.player_config.spawn_interval["min"] / skill.spawn_speed_multiplier,
            "max": battle_state.player_config.spawn_interval["max"] / skill.spawn_speed_multiplier
        }
        
        # 计算所有激活技能的总倍率（该技能在加入字典前，可以等于这个默认值）
        total_multiplier = skill.spawn_speed_multiplier
        # 计算不可重复技能的总倍率
        for active_skill in battle_state.active_single_skills.values():
            total_multiplier *= active_skill.spawn_speed_multiplier
        # 计算可重复技能的总倍率
        for skill_list in battle_state.active_repeat_skills.values():
            for s in skill_list:
                total_multiplier *= s.spawn_speed_multiplier
        
        # battle_state.battle_log.append(
        #     f"触发肉鸽技能: {skill.name} (生成速度提升 {skill.spawn_speed_multiplier}倍)"
        #     f"\n当前生成间隔: {battle_state.player_config.spawn_interval['min']:.2f} - {battle_state.player_config.spawn_interval['max']:.2f}"
        #     f"\n总速度倍率: {total_multiplier:.2f}倍"
        # )
        
        # 根据技能是否可重复，添加到相应的字典中
        if skill.is_repeatable:
            if skill_name not in battle_state.active_repeat_skills:
                battle_state.active_repeat_skills[skill_name] = []
            battle_state.active_repeat_skills[skill_name].append(skill)
        else:
            battle_state.active_single_skills[skill_name] = skill
        
        # 记录技能属性
        skill_attrs = {
            "hp_multiplier": skill.hp_multiplier,
            "attack_multiplier": skill.attack_multiplier,
            "attack_speed_multiplier": skill.attack_speed_multiplier,
            "spawn_speed_multiplier": skill.spawn_speed_multiplier,
            "duration": skill.duration,
            "is_permanent": skill.is_permanent,
            "is_repeatable": skill.is_repeatable
        }
        
        # 触发肉鸽技能事件
        self._emit_event(RogueSkillEvent(
            event_type="rogue_skill",
            timestamp=time.time(),
            data={},
            skill_name=skill_name,
            affected_units=affected_units,
            skill_attributes=skill_attrs
        ))
        
        # 记录肉鸽技能日志
        logger.log_rogue_skill(skill_name, skill_attrs, affected_units, 1)
    
    def handle_keyboard_input(self, battle_state: BattleState, key: str) -> None:
        """处理键盘输入"""
        if key == " " and battle_state.keyboard_spawn_cooldown <= 0:
            self._spawn_player_unit(battle_state)  # 这里会触发我方单位生成事件
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
            is_repeatable=skill_config.get("is_repeatable", False),  # 从配置中获取是否可重复
            start_time=time.time()
        )
        
        # 应用技能效果到所有玩家单位
        affected_units = []
        for unit in battle_state.player_units:
            if unit.state != UnitState.DEAD:
                # 基于初始属性计算强化后的属性
                unit.hp += unit.initial_attrs["hp"] * skill.hp_multiplier
                unit.max_hp += unit.initial_attrs["max_hp"] * skill.hp_multiplier
                unit.attack += unit.initial_attrs["attack"] * skill.attack_multiplier
                unit.attack_speed += unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
                affected_units.append(unit)
        
        # 应用生成速度倍率
        battle_state.player_config.spawn_interval = {
            "min": battle_state.player_config.spawn_interval["min"] / skill.spawn_speed_multiplier,
            "max": battle_state.player_config.spawn_interval["max"] / skill.spawn_speed_multiplier
        }
        
        # 根据技能是否可重复，添加到相应的字典中
        if skill.is_repeatable:
            if "average_rogue_skill" not in battle_state.active_repeat_skills:
                battle_state.active_repeat_skills["average_rogue_skill"] = []
            battle_state.active_repeat_skills["average_rogue_skill"].append(skill)
        else:
            battle_state.active_single_skills["average_rogue_skill"] = skill
        
        # 记录技能属性
        skill_attrs = {
            "hp_multiplier": skill.hp_multiplier,
            "attack_multiplier": skill.attack_multiplier,
            "attack_speed_multiplier": skill.attack_speed_multiplier,
            "spawn_speed_multiplier": skill.spawn_speed_multiplier,
            "duration": skill.duration,
            "is_permanent": skill.is_permanent,
            "is_repeatable": skill.is_repeatable
        }
        
        # 触发肉鸽技能事件
        self._emit_event(RogueSkillEvent(
            event_type="rogue_skill",
            timestamp=time.time(),
            data={},
            skill_name="average_rogue_skill",
            affected_units=affected_units,
            skill_attributes=skill_attrs
        ))
        
        battle_state.battle_log.append(f"触发肉鸽技能: {skill.name} (生成速度提升 {skill.spawn_speed_multiplier}倍)")
    
    def _spawn_units(self, battle_state: BattleState, delta_time: float) -> None:
        """生成单位的条件"""
        current_time = time.time()
        
        # 生成敌方单位
        if battle_state.current_wave < len(battle_state.wave_configs):
            wave = battle_state.wave_configs[battle_state.current_wave]
            if wave.unit_count > 0:
                if 'enemy_spawn' not in battle_state.last_spawn_time:
                    battle_state.last_spawn_time['enemy_spawn'] = current_time
                    self._spawn_enemy_unit(battle_state, wave)
                    wave.unit_count -= 1
                elif current_time - battle_state.last_spawn_time['enemy_spawn'] >= wave.spawn_interval:
                    self._spawn_enemy_unit(battle_state, wave)
                    wave.unit_count -= 1
                    battle_state.last_spawn_time['enemy_spawn'] = current_time
                    
                    if wave.unit_count == 0:
                        battle_state.current_wave += 1
        
        # 生成玩家单位
        if 'player_spawn' not in battle_state.last_spawn_time:
            battle_state.last_spawn_time['player_spawn'] = current_time
            self._spawn_player_unit(battle_state)
        else:
            spawn_interval = random.uniform(
                battle_state.player_config.spawn_interval['min'],
                battle_state.player_config.spawn_interval['max']
            )
            
            if current_time - battle_state.last_spawn_time['player_spawn'] >= spawn_interval:
                self._spawn_player_unit(battle_state)
                battle_state.last_spawn_time['player_spawn'] = current_time
                battle_state.units_spawned_since_enhance += 1
    
    def _spawn_enemy_unit(self, battle_state: BattleState, wave: WaveConfig) -> None:
        """生成敌方单位"""
        unit_config = wave.unit_config
        
        # 记录单位属性
        unit_attrs = {
            "hp": unit_config['hp'],
            "max_hp": unit_config['hp'],
            "attack": unit_config['attack'],
            "attack_speed": unit_config['attack_speed'],
            "attack_range": unit_config['attack_range'],
            "move_speed": unit_config['move_speed'],
            "tower_damage": unit_config['tower_damage']
        }

        # 将FrozenPosition转换为Position
        spawn_position = Position(x=wave.spawn_position.x, y=wave.spawn_position.y)
        
        # 只在调试级别输出详细信息
        logger.log(f"wave中的生成位置: x={wave.spawn_position.x}, y={wave.spawn_position.y}", 3)
        logger.log(f"\n敌方单位生成信息:", 3)
        logger.log(f"波次ID: {wave.wave_id}", 3)
        logger.log(f"生成位置: x={spawn_position.x}, y={spawn_position.y}", 3)
        logger.log(f"单位类型: {wave.unit_type}", 3)
        logger.log(f"单位等级: {wave.unit_level}", 3)
        
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
            tower_damage=unit_config['tower_damage'],
            position=spawn_position
        )
        
        # 只在调试级别输出详细信息
        logger.log(f"单位生成后位置: x={unit.position.x}, y={unit.position.y}", 3)
        logger.log(f"单位ID: {unit.id}", 3)
        logger.log("-" * 50, 3)
        
        battle_state.enemy_units.append(unit)
        
        # 触发敌方单位生成事件
        self._emit_event(EnemyUnitSpawnEvent(
            event_type="enemy_unit_spawn",
            timestamp=time.time(),
            data={},
            unit=unit,
            unit_attributes=unit_attrs.copy()
        ))
        
        # 记录单位生成日志
        logger.log_unit_spawn(unit, unit_attrs, 2)
    
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
            "attack_speed": unit_config['attack_speed'],
            "attack_range": unit_config['attack_range'],
            "move_speed": unit_config['move_speed'],
            "tower_damage": unit_config['tower_damage']
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
            tower_damage=unit_config['tower_damage'],
            position=Position(spawn_x, spawn_y),
            initial_attrs=initial_attrs
        )
        
        # 应用所有当前激活的肉鸽技能效果
        # 应用不可重复技能效果
        for skill in battle_state.active_single_skills.values():
            unit.hp += unit.initial_attrs["hp"] * skill.hp_multiplier
            unit.max_hp += unit.initial_attrs["max_hp"] * skill.hp_multiplier
            unit.attack += unit.initial_attrs["attack"] * skill.attack_multiplier
            unit.attack_speed += unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
        
        # 应用可重复技能效果
        for skill_list in battle_state.active_repeat_skills.values():
            for skill in skill_list:
                unit.hp += unit.initial_attrs["hp"] * skill.hp_multiplier
                unit.max_hp += unit.initial_attrs["max_hp"] * skill.hp_multiplier
                unit.attack += unit.initial_attrs["attack"] * skill.attack_multiplier
                unit.attack_speed += unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
        
        battle_state.player_units.append(unit)
        
        # 触发我方单位生成事件
        self._emit_event(PlayerUnitSpawnEvent(
            event_type="player_unit_spawn",
            timestamp=time.time(),
            data={},
            unit=unit,
            unit_attributes=initial_attrs.copy()
        ))
    
    def _update_units(self, battle_state: BattleState, delta_time: float) -> None:
        """更新单位Buff和行为"""
        current_time = time.time()
        
        # 更新肉鸽技能状态，去掉过期肉鸽技能效果
        self._update_rogue_skills(battle_state, current_time)
        
        # 更新玩家单位
        for unit in battle_state.player_units:
            if unit.state == UnitState.DEAD:
                continue
            
            # 更新单位行为
            self._update_unit_behavior(unit, battle_state, delta_time)
        
        # 更新敌方单位
        for unit in battle_state.enemy_units:
            if unit.state == UnitState.DEAD:
                continue
            self._update_unit_behavior(unit, battle_state, delta_time)
    
    def _find_targets_in_range(self, unit: Unit, battle_state: BattleState) -> List[Unit]:
        """寻找攻击范围内的目标
        
        Args:
            unit: 当前单位
            battle_state: 战斗状态
            
        Returns:
            List[Unit]: 攻击范围内的目标列表
        """
        # 获取敌方单位列表
        if unit.type == UnitType.PLAYER:
            potential_targets = battle_state.enemy_units
        else:
            potential_targets = battle_state.player_units
            
        # 检查是否有敌方单位在攻击范围内
        targets_in_range = []
        for target in potential_targets:
            if target.state != UnitState.DEAD:  # 排除已死亡的单位
                distance = self._calculate_distance(unit.position, target.position)
                if distance <= unit.attack_range:
                    targets_in_range.append(target)
                    
        return targets_in_range

    def _select_target(self, unit: Unit, battle_state: BattleState) -> Optional[Unit]:
        """选择目标（防御塔或其他单位）
        
        Args:
            unit: 当前单位
            battle_state: 战斗状态
            
        Returns:
            Optional[Unit]: 选择的目标，如果没有目标返回None
        """
        # 获取敌方防御塔
        if unit.type == UnitType.PLAYER:
            enemy_tower = battle_state.enemy_tower
        else:
            enemy_tower = battle_state.player_tower
        
        # 如果防御塔不存在或已死亡，返回None
        if not enemy_tower or enemy_tower.state == UnitState.DEAD:
            return None
            
        # 寻找攻击范围内的目标
        targets_in_range = self._find_targets_in_range(unit, battle_state)
        
        # 如果找到目标
        if targets_in_range:
            # 如果只有一个目标，直接选择它
            if len(targets_in_range) == 1:
                selected_target = targets_in_range[0]
            else:
                # 如果有多个目标，随机选择一个
                selected_target = random.choice(targets_in_range)
            
            # battle_state.battle_log.append(f"{unit.id} 发现目标 {selected_target.id}")
            return selected_target
        else:
            # 如果没有找到目标，选择防御塔
            # battle_state.battle_log.append(f"{unit.id} 开始向防御塔移动")
            return enemy_tower

    def _update_unit_behavior(self, unit: Unit, battle_state: BattleState, delta_time: float) -> None:
        """更新单位行为
        
        完整的角色行为逻辑：
        1. 在闲置或无目标时，选择目标
        2. 选择目标后如果目标是防御塔则朝着防御塔移动
        3. 在朝着防御塔移动的过程中需要不停检测是否有敌人进入攻击范围
        4. 有敌人进入攻击范围则攻击，无则继续移动
        5. 敌人进入攻击范围后，如果死亡，则重新选择目标
        """
        # 获取当前目标
        current_target = None
        if unit.target_id:
            current_target = self._get_unit_by_id(unit.target_id, battle_state)
            
        # 如果没有目标或目标已死亡，需要重新选择目标
        if not current_target or current_target.state == UnitState.DEAD:
            unit.target_id = None
            unit.state = UnitState.IDLE
            current_target = self._select_target(unit, battle_state)
            if current_target:
                unit.target_id = current_target.id
                unit.state = UnitState.MOVING
            else:
                # 如果没有可用的目标，单位直接消失
                unit.state = UnitState.DEAD
                battle_state.battle_log.append(f"{unit.id} 发现目标已不存在，消失")
                return
        
        # 检查攻击范围内是否有敌人
        targets_in_range = self._find_targets_in_range(unit, battle_state)
        
        # 如果有敌人进入攻击范围，优先攻击敌人
        if targets_in_range:
            # 选择最近的目标进行攻击
            closest_target = min(targets_in_range, 
                               key=lambda t: self._calculate_distance(unit.position, t.position))
            self._attack_target(unit, closest_target, battle_state)
            return
            
        # 如果没有敌人进入攻击范围，继续向目标移动
        if current_target:
            distance = self._calculate_distance(unit.position, current_target.position)
            
            # 如果目标是防御塔
            if current_target.type == UnitType.TOWER:
                # 如果已经到达防御塔位置
                if distance <= 0.1:  # 使用一个很小的阈值来判断是否到达
                    self._attack_target(unit, current_target, battle_state)
                else:
                    # 继续向防御塔移动
                    self._move_towards_target(unit, current_target, delta_time)
            else:
                # 如果是普通单位，检查是否在攻击范围内
                if distance <= unit.attack_range:
                    self._attack_target(unit, current_target, battle_state)
                else:
                    # 不在攻击范围内，继续移动
                    self._move_towards_target(unit, current_target, delta_time)
    
    def _attack_target(self, unit: Unit, target: Unit, battle_state: BattleState) -> None:
        """攻击目标"""
        # 如果目标是防御塔
        if target.type == UnitType.TOWER:
            # 计算到防御塔的距离
            distance_to_tower = self._calculate_distance(unit.position, target.position)
            
            # 如果到达防御塔位置
            if distance_to_tower <= 0.1:  # 使用一个很小的阈值来判断是否到达
                # 对防御塔造成伤害
                tower_damage = unit.tower_damage  # 使用单位的攻击力作为对塔伤害
                target.hp -= tower_damage
                
                battle_state.battle_log.append(
                    f"{unit.id} 到达防御塔位置，造成 {tower_damage} 点伤害"
                )
                
                # 单位消失
                unit.state = UnitState.DEAD
                battle_state.battle_log.append(f"{unit.id} 撞塔后消失")
                
                # 检查防御塔是否被摧毁
                if target.hp <= 0:
                    target.state = UnitState.DEAD
                    battle_state.battle_log.append(f"防御塔被摧毁！")
            return
            
        # 对普通单位的攻击逻辑
        current_time = time.time()
        
        # 检查攻击冷却
        if current_time - unit.last_attack_time < 1.0 / unit.attack_speed:
            return  # 如果还在冷却中，不执行攻击
            
        unit.state = UnitState.ATTACKING
        unit.last_attack_time = current_time
        
        damage = unit.attack  # 使用战斗公式计算伤害
        target.hp -= damage
        
        # 触发伤害事件
        self._emit_event(DamageEvent(
            event_type="damage",
            timestamp=current_time,
            data={},
            attacker=unit,
            target=target,
            damage=damage
        ))
        
        # 记录伤害日志
        logger.log_damage(unit, target, damage, 2)
        
        if target.hp <= 0:
            target.state = UnitState.DEAD
            
            # 触发单位死亡事件
            self._emit_event(UnitDeathEvent(
                event_type="unit_death",
                timestamp=current_time,
                data={},
                unit=target,
                killer_id=unit.id
            ))
            
            # 记录单位死亡日志
            logger.log_unit_death(target, unit.id, 1)
            
            # 目标死亡后，重新寻找目标
            unit.target_id = None
            unit.state = UnitState.IDLE
            self._select_target(unit, battle_state)  # 立即寻找新目标
    
    def _move_towards_target(self, unit: Unit, target: Unit, delta_time: float) -> None:
        """向目标移动
        
        Args:
            unit: 要移动的单位
            target: 目标单位
            delta_time: 时间增量（秒）
        """
        unit.state = UnitState.MOVING
        direction_x = target.position.x - unit.position.x
        direction_y = target.position.y - unit.position.y
        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
        
        if distance > 0:
            # 在游戏坐标系中移动，不需要考虑POSITION_SCALE
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
            self._emit_battle_end_event(battle_state)
            return
        
        if battle_state.enemy_tower and battle_state.enemy_tower.hp <= 0:
            battle_state.game_over = True
            battle_state.winner = "player"
            self._emit_battle_end_event(battle_state)
            return
        
        # 检查敌方单位是否全部死亡
        # 如果当前波次已经完成（current_wave >= len(wave_configs)）且没有存活的敌方单位
        if (battle_state.current_wave >= len(battle_state.wave_configs) and 
            not any(unit.state != UnitState.DEAD for unit in battle_state.enemy_units)):
            battle_state.game_over = True
            battle_state.winner = "player"
            self._emit_battle_end_event(battle_state)
            return
    
    def _generate_battle_result(self, battle_state: BattleState) -> BattleResult:
        """生成战斗结果"""
        # 计算存活的单位数量
        player_units_alive = len([u for u in battle_state.player_units if u.state != UnitState.DEAD])
        enemy_units_alive = len([u for u in battle_state.enemy_units if u.state != UnitState.DEAD])
        
        # 获取防御塔血量
        player_tower_hp = battle_state.player_tower.hp if battle_state.player_tower else 0
        enemy_tower_hp = battle_state.enemy_tower.hp if battle_state.enemy_tower else 0
        
        return BattleResult(
            winner=battle_state.winner,
            total_duration=time.time() - battle_state.start_time,
            player_tower_hp=player_tower_hp,
            enemy_tower_hp=enemy_tower_hp,
            player_units_alive=player_units_alive,
            enemy_units_alive=enemy_units_alive,
            battle_log=battle_state.battle_log
        )
    
    def _update_rogue_skills(self, battle_state: BattleState, current_time: float) -> None:
        """更新肉鸽技能状态"""
        # 检查不可重复技能是否过期
        expired_single_skills = []
        for skill_name, skill in battle_state.active_single_skills.items():
            if not skill.is_permanent and skill.is_expired(current_time):
                expired_single_skills.append(skill_name)
                # 移除技能效果
                for unit in battle_state.player_units:
                    if unit.state != UnitState.DEAD:
                        unit.hp -= unit.initial_attrs["hp"] * skill.hp_multiplier
                        unit.max_hp -= unit.initial_attrs["max_hp"] * skill.hp_multiplier
                        unit.attack -= unit.initial_attrs["attack"] * skill.attack_multiplier
                        unit.attack_speed -= unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
                # 回退生成速度倍率
                battle_state.player_config.spawn_interval = {
                    "min": battle_state.player_config.spawn_interval["min"] * skill.spawn_speed_multiplier,
                    "max": battle_state.player_config.spawn_interval["max"] * skill.spawn_speed_multiplier
                }
                battle_state.battle_log.append(f"肉鸽技能 {skill.name} 已过期")
        
        # 移除过期的不可重复技能
        for skill_name in expired_single_skills:
            del battle_state.active_single_skills[skill_name]
        
        # 检查可重复技能是否过期
        expired_repeat_skills = []
        for skill_name, skill_list in battle_state.active_repeat_skills.items():
            expired_indices = []
            for i, skill in enumerate(skill_list):
                if not skill.is_permanent and skill.is_expired(current_time):
                    expired_indices.append(i)
                    # 移除技能效果
                    for unit in battle_state.player_units:
                        if unit.state != UnitState.DEAD:
                            unit.hp -= unit.initial_attrs["hp"] * skill.hp_multiplier
                            unit.max_hp -= unit.initial_attrs["max_hp"] * skill.hp_multiplier
                            unit.attack -= unit.initial_attrs["attack"] * skill.attack_multiplier
                            unit.attack_speed -= unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
                    # 回退生成速度倍率
                    battle_state.player_config.spawn_interval = {
                        "min": battle_state.player_config.spawn_interval["min"] * skill.spawn_speed_multiplier,
                        "max": battle_state.player_config.spawn_interval["max"] * skill.spawn_speed_multiplier
                    }
                    battle_state.battle_log.append(f"肉鸽技能 {skill.name} 已过期")
            
            # 从后向前删除过期的技能，避免索引变化
            for i in sorted(expired_indices, reverse=True):
                del skill_list[i]
            
            # 如果列表为空，删除整个技能条目
            if not skill_list:
                expired_repeat_skills.append(skill_name)
        
        # 移除空的可重复技能列表
        for skill_name in expired_repeat_skills:
            del battle_state.active_repeat_skills[skill_name]
    
    def _emit_battle_end_event(self, battle_state: BattleState) -> None:
        """触发战斗结束事件"""
        duration = time.time() - battle_state.start_time
        self._emit_event(BattleEndEvent(
            event_type="battle_end",
            timestamp=time.time(),
            data={},
            winner=battle_state.winner,
            duration=duration
        ))
        
        # 记录战斗结束日志
        logger.log_battle_end(battle_state.winner, duration, 1)
        
        self.statistics.end_battle(battle_state.winner)
        stats = self.statistics.calculate_statistics()
        self.data_exporter.save_battle_data(stats) 