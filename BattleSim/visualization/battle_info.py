"""
战斗信息显示模块
"""

from typing import List, Dict, Tuple
from ..models.battle_state import BattleState
from ..statistics import BattleStatistics

class BattleInfoCalculator:
    """战斗信息计算器"""
    
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