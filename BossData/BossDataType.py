"""Boss相关的数据类型"""

from enum import Enum
from typing import List, Dict, Any


class 战斗Boss:
    def __init__(self, 怪物数据: Dict[str, Any], 血量倍数: float = 10, 攻击力倍数: float = 3):
        self.怪物数据 = 怪物数据
        self.血量倍数 = 血量倍数
        self.攻击力倍数 = 攻击力倍数
        self.对塔伤害 = 20  # 战斗型boss对塔伤害固定为20


class 技能Boss:
    def __init__(self, 名称: str, 编号: str, 技能等级: int, 血量: float, 移动速度: float = 1.2, 适配地图: List[str] = None, 对塔伤害: int = 0):
        self.名称 = 名称
        self.编号 = 编号
        self.技能等级 = 技能等级
        self.血量 = 血量
        self.移动速度 = 移动速度  # 技能Boss的移动速度默认为1.2
        self.适配地图 = 适配地图 if 适配地图 is not None else []  # 技能Boss的适配地图默认为空列表
        self.对塔伤害 = 对塔伤害  # 技能Boss的对塔伤害默认为0
    

    
