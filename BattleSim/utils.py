"""
工具函数模块
"""

import random
from typing import Dict, List, Any, Optional
import json
import logging

def setup_logging(log_level: str = 'INFO') -> None:
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"配置文件 {config_path} 不存在，使用默认配置")
        return {}

def save_config(config: Dict[str, Any], config_path: str) -> None:
    """保存配置到文件"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def set_random_seed(seed: Optional[int] = None) -> None:
    """设置随机种子"""
    if seed is not None:
        random.seed(seed)

def format_battle_log(log_entries: List[str]) -> str:
    """格式化战斗日志"""
    return '\n'.join(log_entries)

def calculate_percentage(value: float, total: float) -> float:
    """计算百分比"""
    return (value / total) * 100 if total != 0 else 0

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """合并两个字典"""
    result = dict1.copy()
    result.update(dict2)
    return result 