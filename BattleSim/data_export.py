"""
战斗数据导出模块
负责将战斗统计数据保存到JSON文件
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from .models.statistics_data import StatisticsData

class BattleDataExporter:
    def __init__(self, save_dir: str = "battle_records"):
        """
        初始化数据导出器
        
        Args:
            save_dir: 保存战斗记录的目录
        """
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳字符串"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _convert_to_dict(self, stats: StatisticsData) -> Dict[str, Any]:
        """将统计数据转换为字典格式"""
        return {
            "battle_info": {
                "duration": stats.battle_duration,
                "winner": stats.winner,
                "timestamp": self._get_timestamp()
            },
            "unit_stats": {
                "player": {
                    "spawn_count": stats.player_unit_spawns,
                    "death_count": stats.unit_deaths["player"],
                    "unit_details": stats.player_unit_details
                },
                "enemy": {
                    "spawn_count": stats.enemy_unit_spawns,
                    "death_count": stats.unit_deaths["enemy"],
                    "unit_details": stats.enemy_unit_details
                }
            },
            "damage_stats": {
                "player": {
                    "dealt": stats.damage_dealt["player"],
                    "taken": stats.damage_taken["player"]
                },
                "enemy": {
                    "dealt": stats.damage_dealt["enemy"],
                    "taken": stats.damage_taken["enemy"]
                }
            },
            "rogue_skills": {
                "count": stats.rogue_skill_count,
                "details": stats.rogue_skill_details
            },
            "time_series": {
                "unit_counts": stats.unit_count_time_series,
                "power": stats.power_time_series,
                "damage": stats.damage_time_series
            }
        }
    
    def save_battle_data(self, stats: StatisticsData, filename: Optional[str] = None) -> str:
        """
        保存战斗数据到JSON文件
        
        Args:
            stats: 战斗统计数据
            filename: 可选的文件名，如果不指定则使用时间戳
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"battle_{self._get_timestamp()}.json"
        
        filepath = os.path.join(self.save_dir, filename)
        data = self._convert_to_dict(stats)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    @staticmethod
    def load_battle_data(filepath: str) -> Dict[str, Any]:
        """
        从JSON文件加载战斗数据
        
        Args:
            filepath: JSON文件路径
            
        Returns:
            战斗数据字典
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_battle_records(self) -> List[str]:
        """
        列出所有战斗记录文件
        
        Returns:
            战斗记录文件名列表
        """
        return [f for f in os.listdir(self.save_dir) if f.endswith('.json')] 