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
from .utils import set_random_seed, format_battle_log
from .battle_events import (
    BattleEvent, PlayerUnitSpawnEvent, EnemyUnitSpawnEvent, UnitDeathEvent,
    DamageEvent, RogueSkillEvent, BattleEndEvent
)
from .statistics import BattleStatistics
from .data_export import BattleDataExporter

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
            active_rogue_skills={},
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
        print(f"\n当前战斗状态:")
        print(f"我方单位数量: {len(battle_state.player_units)}")
        print(f"敌方单位数量: {len(battle_state.enemy_units)}")
        print(f"当前波次: {battle_state.current_wave + 1}/{len(battle_state.wave_configs)}")
        
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
        
        # 输出战斗日志
        if battle_state.battle_log:
            print("\n战斗日志:")
            for log in battle_state.battle_log[-5:]:  # 只显示最近的5条日志
                print(log)
    
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
        
        battle_state.active_rogue_skills[skill_name] = skill
        battle_state.battle_log.append(f"触发肉鸽技能: {skill.name} (生成速度提升 {skill.spawn_speed_multiplier}倍)")
        
        # 记录技能属性
        skill_attrs = {
            "hp_multiplier": skill.hp_multiplier,
            "attack_multiplier": skill.attack_multiplier,
            "attack_speed_multiplier": skill.attack_speed_multiplier,
            "spawn_speed_multiplier": skill.spawn_speed_multiplier,
            "duration": skill.duration,
            "is_permanent": skill.is_permanent
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
        
        battle_state.active_rogue_skills["average_rogue_skill"] = skill
        
        # 记录技能属性
        skill_attrs = {
            "hp_multiplier": skill.hp_multiplier,
            "attack_multiplier": skill.attack_multiplier,
            "attack_speed_multiplier": skill.attack_speed_multiplier,
            "spawn_speed_multiplier": skill.spawn_speed_multiplier,
            "duration": skill.duration,
            "is_permanent": skill.is_permanent
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
        """生成单位"""
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
            position=wave.spawn_position
        )
        battle_state.enemy_units.append(unit)
        battle_state.battle_log.append(f"敌方单位 {unit.id} 已生成")
        
        # 触发敌方单位生成事件
        self._emit_event(EnemyUnitSpawnEvent(
            event_type="enemy_unit_spawn",
            timestamp=time.time(),
            data={},
            unit=unit,
            unit_attributes=unit_attrs.copy()
        ))
    
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
        for skill_name, skill in battle_state.active_rogue_skills.items():
            unit.hp += unit.initial_attrs["hp"] * skill.hp_multiplier
            unit.max_hp += unit.initial_attrs["max_hp"] * skill.hp_multiplier
            unit.attack += unit.initial_attrs["attack"] * skill.attack_multiplier
            unit.attack_speed += unit.initial_attrs["attack_speed"] * skill.attack_speed_multiplier
        
        battle_state.player_units.append(unit)
        battle_state.battle_log.append(f"玩家单位 {unit.id} 已生成")
        
        # 触发我方单位生成事件
        self._emit_event(PlayerUnitSpawnEvent(
            event_type="player_unit_spawn",
            timestamp=time.time(),
            data={},
            unit=unit,
            unit_attributes=initial_attrs.copy()
        ))
    
    def _update_units(self, battle_state: BattleState, delta_time: float) -> None:
        """更新单位身上的Buff状态"""
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
        # 获取敌方防御塔
        if unit.type == UnitType.PLAYER:
            enemy_tower = battle_state.enemy_tower
        else:
            enemy_tower = battle_state.player_tower
        
        # 如果防御塔存在且未死亡
        if enemy_tower and enemy_tower.state != UnitState.DEAD:
            # 计算到防御塔的距离
            distance_to_tower = self._calculate_distance(unit.position, enemy_tower.position)
            
            # 如果到达防御塔位置
            if distance_to_tower <= 0.1:  # 使用一个很小的阈值来判断是否到达
                # 对防御塔造成伤害
                tower_damage = unit.tower_damage  # 使用单位的攻击力作为对塔伤害
                enemy_tower.hp -= tower_damage
                
                battle_state.battle_log.append(
                    f"{unit.id} 到达防御塔位置，造成 {tower_damage} 点伤害"
                )
                
                # 单位消失
                unit.state = UnitState.DEAD
                battle_state.battle_log.append(f"{unit.id} 撞塔后消失")
                
                # 检查防御塔是否被摧毁
                if enemy_tower.hp <= 0:
                    enemy_tower.state = UnitState.DEAD
                    battle_state.battle_log.append(f"防御塔被摧毁！")
            else:
                # 如果没有目标或处于空闲状态，寻找新目标
                if not unit.target_id or unit.state == UnitState.IDLE:
                    self._find_target(unit, battle_state)
                
                # 如果有当前目标，处理移动或攻击
                if unit.target_id:
                    target = self._get_unit_by_id(unit.target_id, battle_state)
                    if target:
                        distance = self._calculate_distance(unit.position, target.position)
                        if distance <= unit.attack_range:
                            self._attack_target(unit, target, battle_state)
                            # 如果目标死亡，继续向防御塔移动
                            if target.state == UnitState.DEAD:
                                unit.target_id = enemy_tower.id
                                unit.state = UnitState.MOVING
                        else:
                            self._move_towards_target(unit, target, delta_time)
                    else:
                        # 如果目标不存在，继续向防御塔移动
                        unit.target_id = enemy_tower.id
                        unit.state = UnitState.MOVING
        else:
            # 如果没有防御塔或防御塔已死亡，单位直接消失
            unit.state = UnitState.DEAD
            battle_state.battle_log.append(f"{unit.id} 发现目标已不存在，消失")
    
    def _find_target(self, unit: Unit, battle_state: BattleState) -> None:
        """寻找目标（防御塔或其他单位）"""
        # 获取敌方防御塔
        if unit.type == UnitType.PLAYER:
            enemy_tower = battle_state.enemy_tower
            potential_targets = battle_state.enemy_units
        else:
            enemy_tower = battle_state.player_tower
            potential_targets = battle_state.player_units
        
        # 如果防御塔存在且未死亡
        if enemy_tower and enemy_tower.state != UnitState.DEAD:
            # 寻找攻击范围内的目标
            targets_in_range = []
            for target in potential_targets:
                if target.state != UnitState.DEAD and target != enemy_tower:  # 排除防御塔
                    distance = self._calculate_distance(unit.position, target.position)
                    if distance <= unit.attack_range:
                        targets_in_range.append(target)
            
            # 如果找到目标
            if targets_in_range:
                # 如果只有一个目标，直接选择它
                if len(targets_in_range) == 1:
                    unit.target_id = targets_in_range[0].id
                else:
                    # 如果有多个目标，随机选择一个
                    selected_target = random.choice(targets_in_range)
                    unit.target_id = selected_target.id
                
                unit.state = UnitState.MOVING
                battle_state.battle_log.append(f"{unit.id} 发现目标 {unit.target_id}")
            else:
                # 如果没有找到目标，选择防御塔
                unit.target_id = enemy_tower.id
                unit.state = UnitState.MOVING
                battle_state.battle_log.append(f"{unit.id} 开始向防御塔移动")
        else:
            # 如果没有防御塔或防御塔已死亡，单位直接消失
            unit.state = UnitState.DEAD
            battle_state.battle_log.append(f"{unit.id} 发现目标已不存在，消失")
    
    def _attack_target(self, unit: Unit, target: Unit, battle_state: BattleState) -> None:
        """攻击目标"""
        current_time = time.time()
        
        # 检查攻击冷却
        if current_time - unit.last_attack_time < 1.0 / unit.attack_speed:
            return  # 如果还在冷却中，不执行攻击
            
        unit.state = UnitState.ATTACKING
        unit.last_attack_time = current_time
        
        damage = unit.attack  # 使用战斗公式计算伤害
        target.hp -= damage
        
        battle_state.battle_log.append(
            f"{unit.id} 对 {target.id} 造成 {damage} 点伤害"
        )
        
        # 触发伤害事件
        self._emit_event(DamageEvent(
            event_type="damage",
            timestamp=current_time,
            data={},
            attacker=unit,
            target=target,
            damage=damage
        ))
        
        if target.hp <= 0:
            target.state = UnitState.DEAD
            battle_state.battle_log.append(f"{target.id} 已死亡")
            
            # 触发单位死亡事件
            self._emit_event(UnitDeathEvent(
                event_type="unit_death",
                timestamp=current_time,
                data={},
                unit=target,
                killer_id=unit.id
            ))
            
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
            self._emit_battle_end_event(battle_state)
            return
        
        if battle_state.enemy_tower and battle_state.enemy_tower.hp <= 0:
            battle_state.game_over = True
            battle_state.winner = "player"
            self._emit_battle_end_event(battle_state)
            return
        
        # 检查单位
        if not battle_state.player_units and not battle_state.enemy_units:
            battle_state.game_over = True
            battle_state.winner = "draw"
            self._emit_battle_end_event(battle_state)
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
    
    def _emit_battle_end_event(self, battle_state: BattleState) -> None:
        """触发战斗结束事件"""
        self._emit_event(BattleEndEvent(
            event_type="battle_end",
            timestamp=time.time(),
            data={},
            winner=battle_state.winner,
            duration=time.time() - battle_state.start_time
        ))
        self.statistics.end_battle(battle_state.winner)
        stats = self.statistics.calculate_statistics()
        self.data_exporter.save_battle_data(stats) 