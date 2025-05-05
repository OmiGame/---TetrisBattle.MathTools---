"""
工具模块
提供各种通用功能
"""

import random
import time
from typing import Dict, List, Any, Optional
import json

class Logger:
    """通用日志工具类"""
    def __init__(self, level: int = 0):
        """初始化日志工具
        Args:
            level: 日志级别 (0: 无日志, 1: 重要信息, 2: 详细信息, 3: 调试信息)
        """
        self.level = level
    
    def set_level(self, level: int) -> None:
        """设置日志级别
        Args:
            level: 日志级别 (0: 无日志, 1: 重要信息, 2: 详细信息, 3: 调试信息)
        """
        self.level = level
    
    def log(self, message: str, level: int = 1) -> None:
        """输出日志
        Args:
            message: 日志消息
            level: 日志级别
        """
        if level <= self.level:
            print(message)
    
    def log_battle_state(self, battle_state: Any) -> None:
        """输出战斗状态日志
        Args:
            battle_state: 战斗状态对象
        """
        if self.level >= 2:
            print(f"\n当前战斗状态:")
            print(f"我方单位数量: {len(battle_state.player_units)}")
            print(f"敌方单位数量: {len(battle_state.enemy_units)}")
            print(f"当前波次: {battle_state.current_wave + 1}/{len(battle_state.wave_configs)}")
    
    def log_battle_log(self, battle_log: List[str], max_lines: int = 30) -> None:
        """输出战斗日志
        Args:
            battle_log: 战斗日志列表
            max_lines: 最大显示行数
        """
        if battle_log and self.level >= 1:
            print("\n战斗日志:")
            for log in battle_log[-max_lines:]:
                print(log)
                
    def log_unit_spawn(self, unit: Any, unit_attributes: Dict[str, Any], level: int = 2) -> None:
        """输出单位生成日志
        Args:
            unit: 单位对象
            unit_attributes: 单位属性字典
            level: 日志级别
        """
        if level <= self.level:
            print(f"\n单位生成信息:")
            print(f"单位ID: {unit.id}")
            print(f"单位类型: {unit.type}")
            print(f"单位等级: {unit.level}")
            print(f"生成位置: x={unit.position.x}, y={unit.position.y}")
            print(f"单位属性: {unit_attributes}")
            
    def log_rogue_skill(self, skill_name: str, skill_attributes: Dict[str, Any], affected_units: List[Any], level: int = 1) -> None:
        """输出肉鸽技能日志
        Args:
            skill_name: 技能名称
            skill_attributes: 技能属性字典
            affected_units: 受影响的单位列表
            level: 日志级别
        """
        if level <= self.level:
            print(f"\n触发肉鸽技能: {skill_name}")
            print(f"技能属性: {skill_attributes}")
            print(f"受影响单位数量: {len(affected_units)}")
            
    def log_unit_death(self, unit: Any, killer_id: str, level: int = 1) -> None:
        """输出单位死亡日志
        Args:
            unit: 死亡单位对象
            killer_id: 击杀者ID
            level: 日志级别
        """
        if level <= self.level:
            print(f"\n单位死亡信息:")
            print(f"死亡单位ID: {unit.id}")
            print(f"击杀者ID: {killer_id}")
            
    def log_damage(self, attacker: Any, target: Any, damage: float, level: int = 2) -> None:
        """输出伤害日志
        Args:
            attacker: 攻击者对象
            target: 目标对象
            damage: 伤害值
            level: 日志级别
        """
        if level <= self.level:
            print(f"\n伤害信息:")
            print(f"攻击者ID: {attacker.id}")
            print(f"目标ID: {target.id}")
            print(f"造成伤害: {damage}")
            
    def log_battle_end(self, winner: str, duration: float, level: int = 1) -> None:
        """输出战斗结束日志
        Args:
            winner: 胜利者
            duration: 战斗持续时间
            level: 日志级别
        """
        if level <= self.level:
            print(f"\n战斗结束:")
            print(f"胜利者: {winner}")
            print(f"战斗持续时间: {duration:.2f}秒")

# 创建全局日志实例
logger = Logger()


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """保存配置到文件"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def set_random_seed(seed: Optional[int] = None) -> None:
    """设置随机数种子"""
    if seed is not None:
        random.seed(seed)
    else:
        random.seed(time.time())

def format_battle_log(log: str) -> str:
    """格式化战斗日志"""
    return f"[{time.strftime('%H:%M:%S')}] {log}"

def calculate_percentage(value: float, total: float) -> float:
    """计算百分比"""
    return (value / total) * 100 if total != 0 else 0

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """合并两个字典"""
    result = dict1.copy()
    result.update(dict2)
    return result 