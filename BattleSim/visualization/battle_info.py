"""
战斗信息计算和显示模块
"""

from typing import List, Dict, Tuple
from ..models.battle_state import BattleState, Unit, UnitState

class BattleInfoCalculator:
    """战斗信息计算器"""
    
    @staticmethod
    def calculate_unit_stats(units: List[Unit]) -> Dict[str, float]:
        """计算单位统计信息"""
        alive_count = sum(1 for u in units if u.state != UnitState.DEAD)
        total_power = sum(unit.attack * unit.hp for unit in units if unit.state != UnitState.DEAD)
        return {
            "alive_count": alive_count,
            "total_power": total_power
        }
    
    @staticmethod
    def calculate_battle_stats(battle_state: BattleState) -> Dict[str, any]:
        """计算战斗统计信息"""
        player_stats = BattleInfoCalculator.calculate_unit_stats(battle_state.player_units)
        enemy_stats = BattleInfoCalculator.calculate_unit_stats(battle_state.enemy_units)
        
        return {
            "player": {
                "alive_units": player_stats["alive_count"],
                "total_power": player_stats["total_power"]
            },
            "enemy": {
                "alive_units": enemy_stats["alive_count"],
                "total_power": enemy_stats["total_power"]
            },
            "rogue_skill_count": len(battle_state.active_rogue_skills)
        }
    
    @staticmethod
    def format_battle_info(battle_stats: Dict[str, any]) -> List[str]:
        """格式化战斗信息为显示文本"""
        return [
            f"我方存活单位: {battle_stats['player']['alive_units']}",
            f"敌方存活单位: {battle_stats['enemy']['alive_units']}",
            f"我方总战力: {battle_stats['player']['total_power']:.1f}",
            f"敌方总战力: {battle_stats['enemy']['total_power']:.1f}",
            f"已触发肉鸽技能: {battle_stats['rogue_skill_count']}次"
        ]
    
    @staticmethod
    def format_battle_result(battle_result) -> Tuple[List[str], List[str]]:
        """格式化战斗结果为显示文本"""
        header_texts = [
            f"战斗结束！胜利者: {battle_result.winner}",
            f"总战斗时长: {battle_result.total_duration:.1f} 秒",
            "",
            "战斗日志:"
        ]
        
        log_texts = battle_result.battle_log[-5:]
        
        return header_texts, log_texts 