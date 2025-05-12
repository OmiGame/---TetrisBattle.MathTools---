from enum import Enum
from dataclasses import dataclass
from typing import Dict, List
import os
import sys

# from BattleFormula import 战斗公式，会导致循环导入报错
sys.path.append(os.path.abspath('Gen'))
import json
from GenCode import schema as schema

def loader(f):
    return json.load(open('GenData/' + f + ".json", 'r', encoding="utf-8"))

tables = schema.cfg_Tables(loader)
怪物设计表 = tables.Tb怪物设计表
怪物基础数据表 = tables.Tb怪物基础数据表_3导


class 怪物职业(Enum):
    """怪物职业划分"""
    坦克 = "坦克"
    近战 = "近战"
    远程 = "远程"
    刺客 = "刺客"

class 怪物品质(Enum):
    """怪物品质划分"""
    普通 = "普通"
    精英 = "精英"


class 地图类型(Enum):
    """地图类型枚举"""
    雪山 = "雪山"
    火山 = "火山"
    森林 = "森林"
    草原 = "草原"

@dataclass
class 怪物基础属性数据:
    """存储怪物的基础属性信息"""
    名称: str
    职业: 怪物职业
    品质: 怪物品质
    怪物编号: int
    适配地图: List[地图类型]
    各等级属性数据: Dict[int, Dict[str, float]]  # 等级 -> 属性字典
    基础攻击速度: float
    基础攻击范围: float
    基础移动速度: float
    血量特效倍率: float
    DPS特效倍率: float
    血量成长倍率: float
    攻击力成长倍率: float
    对塔伤害: int = 1  # 默认值为1

    def __post_init__(self):
        """验证属性值的范围"""
        if not 0 <= self.基础攻击速度 <= 3:
            raise ValueError(f"基础攻击速度必须在0到3之间，当前值: {self.基础攻击速度}")
        
        if not 0 <= self.基础攻击范围 <= 5:
            raise ValueError(f"基础攻击范围必须在0到5之间，当前值: {self.基础攻击范围}")
        
        if not 0 <= self.基础移动速度 <= 3:
            raise ValueError(f"基础移动速度必须在0到3之间，当前值: {self.基础移动速度}")
        
        if not 0 <= self.血量特效倍率 <= 1:
            raise ValueError(f"血量特效倍率必须在0到1之间，当前值: {self.血量特效倍率}")
        
        if not 0 <= self.DPS特效倍率 <= 1:
            raise ValueError(f"DPS特效倍率必须在0到1之间，当前值: {self.DPS特效倍率}")
        
        if not 1 <= self.血量成长倍率 <= 3:
            raise ValueError(f"血量成长倍率必须在0到1之间，当前值: {self.血量成长倍率}")
        
        if not 1 <= self.攻击力成长倍率 <= 3:
            raise ValueError(f"攻击力成长倍率必须在0到1之间，当前值: {self.攻击力成长倍率}")
            
        if not 1 <= self.对塔伤害 <= 5:
            raise ValueError(f"对塔伤害必须在1到5之间，当前值: {self.对塔伤害}")

    def 获取等级属性(self, 等级: int) -> Dict[str, float]:
        """获取指定等级的属性数据"""
        if 等级 not in self.各等级属性数据:
            raise ValueError(f"等级 {等级} 不在有效范围内")
        return self.各等级属性数据[等级]

    def 获取所有等级(self) -> list[int]:
        """获取所有有效的等级"""
        return sorted(self.各等级属性数据.keys())




@dataclass
class 怪物属性比例和期望生命周期:
    """定义怪物在不同战力下的血量和DPS比例"""
    血量比例: float  # 血量占总战力的比例
    DPS比例: float   # DPS占总战力的比例
    期望生存时间: float  # 期望生存时间（秒）

    def __post_init__(self):
        """验证属性比例之和是否等于1"""
        总比例 = self.血量比例 + self.DPS比例
        if abs(总比例 - 1.0) > 0.0001:  # 使用小误差范围来处理浮点数比较
            raise ValueError(f"属性比例之和必须等于1，当前为: {总比例}")

class 怪物设计理论值基本参数:
    """怪物设计的基本参数配置"""
    # 战力系数控制
    最大战力系数 = 1.2
    最小战力系数 = 0.8
    
    # 波次数量控制
    波次数量上限 = 40
    波次数量下限 = 5
    
    # 精英怪对比普通怪战力的差距
    精英怪对比普通怪 = 1.5

    怪物最低等级 = 1
    怪物最高等级 = 20

# 怪物属性配置
怪物属性配置: Dict[tuple[怪物职业, 怪物品质], 怪物属性比例和期望生命周期] = {
    (怪物职业.坦克, 怪物品质.普通): 怪物属性比例和期望生命周期(血量比例=0.8, DPS比例=0.2, 期望生存时间=10),
    (怪物职业.坦克, 怪物品质.精英): 怪物属性比例和期望生命周期(血量比例=0.85, DPS比例=0.15, 期望生存时间=12),
    (怪物职业.近战, 怪物品质.普通): 怪物属性比例和期望生命周期(血量比例=0.6, DPS比例=0.4, 期望生存时间=7),
    (怪物职业.近战, 怪物品质.精英): 怪物属性比例和期望生命周期(血量比例=0.65, DPS比例=0.35, 期望生存时间=8),
    (怪物职业.远程, 怪物品质.普通): 怪物属性比例和期望生命周期(血量比例=0.4, DPS比例=0.6, 期望生存时间=4),
    (怪物职业.远程, 怪物品质.精英): 怪物属性比例和期望生命周期(血量比例=0.45, DPS比例=0.55, 期望生存时间=5),
    (怪物职业.刺客, 怪物品质.普通): 怪物属性比例和期望生命周期(血量比例=0.5, DPS比例=0.5, 期望生存时间=5),
    (怪物职业.刺客, 怪物品质.精英): 怪物属性比例和期望生命周期(血量比例=0.55, DPS比例=0.45, 期望生存时间=6)
}