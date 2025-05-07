from enum import Enum
from dataclasses import dataclass
from typing import Dict

class 怪物职业(Enum):
    """怪物职业划分"""
    普通坦克 = "普通坦克"
    精英坦克 = "精英坦克"
    普通近战 = "普通近战"
    精英近战 = "精英近战"
    普通远程 = "普通远程"
    精英远程 = "精英远程"
    普通刺客 = "普通刺客"
    精英刺客 = "精英刺客"

@dataclass
class 怪物基础属性数据:
    """存储怪物的基础属性信息"""
    名称: str
    职业: 怪物职业
    各等级属性数据: Dict[int, Dict[str, float]]  # 等级 -> 属性字典
    基础攻击速度: float
    基础攻击范围: float
    基础移动速度: float
    血量特效倍率: float
    DPS特效倍率: float

    def __post_init__(self):
        """验证属性值的范围"""
        if not 0 <= self.基础攻击速度 <= 3:
            raise ValueError(f"基础攻击速度必须在0到5之间，当前值: {self.基础攻击速度}")
        
        if not 0 <= self.基础攻击范围 <= 5:
            raise ValueError(f"基础攻击范围必须在0到5之间，当前值: {self.基础攻击范围}")
        
        if not 0 <= self.基础移动速度 <= 3:
            raise ValueError(f"基础移动速度必须在0到5之间，当前值: {self.基础移动速度}")
        
        if not 0 <= self.血量特效倍率 <= 2:
            raise ValueError(f"血量特效倍率必须在0到2之间，当前值: {self.血量特效倍率}")
        
        if not 0 <= self.DPS特效倍率 <= 2:
            raise ValueError(f"DPS特效倍率必须在0到2之间，当前值: {self.DPS特效倍率}")

    def 获取等级属性(self, 等级: int) -> Dict[str, float]:
        """获取指定等级的属性数据"""
        if 等级 not in self.各等级属性数据:
            raise ValueError(f"等级 {等级} 不在有效范围内")
        return self.各等级属性数据[等级]

    def 获取所有等级(self) -> list[int]:
        """获取所有有效的等级"""
        return sorted(self.各等级属性数据.keys()) 