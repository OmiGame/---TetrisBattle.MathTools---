"""波次的数据类型，基础数据和计算数据分离，先填基础数据，然后通过函数获得计算数据，从而拿到所有配置数据"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Tuple
from LubanData import tables, 全局参数

class 波次体验(Enum):
    """波次体验枚举"""
    轻松 = "轻松"
    一般 = "一般"
    困难 = "困难"
    地狱 = "地狱"
    Boss = "Boss"

# 不同波次体验类型对应的波盈缺换算成英雄的合理范围
波盈缺范围: Dict[波次体验, Tuple[float, float]] = {
    波次体验.轻松: (-8, -4),  # 轻松：负值较小，表示相对容易
    波次体验.一般: (-5, 5),   # 一般：接近平衡
    波次体验.困难: (0, 10),    # 困难：正值较小，表示稍微困难
    波次体验.地狱: (2, 12),    # 地狱：正值较大，表示非常困难
    波次体验.Boss: (-10, 10)     # Boss：正值中等，因为Boss不在战力计算范围中，所以其他怪物差不多就行，主要是纯战斗的boss的战力计算
}

@dataclass
class 组基础配置:
    """怪物组配置"""
    怪物名称: str 
    怪物编号: int    
    数量: int         
    等级: int        
    是否Boss: bool      
    组内间隔: float  
    组间间隔: float   
    生成位置: float  
    Boss血量: Optional[float] = None  
    

@dataclass
class 组配置(组基础配置):
    @property
    def 组战力总值(self) -> float:
        """计算波次总战力值"""
        if not hasattr(self, '_组战力总值'):
            # 计算所有怪物组的战力总和
            self._组战力总值 = tables.Tb怪物基础数据表_3导.get(f"{self.怪物名称} {self.等级}").战力 * self.数量
        return self._组战力总值
    
    @classmethod
    def 从基础配置创建(cls, 基础配置: 组基础配置) -> '组配置':
        """从基础配置创建完整配置"""
        return cls(
            怪物名称=基础配置.怪物名称,
            怪物编号=基础配置.怪物编号,
            数量=基础配置.数量,
            等级=基础配置.等级,
            是否Boss=基础配置.是否Boss,
            Boss血量=基础配置.Boss血量,
            组内间隔=基础配置.组内间隔,
            组间间隔=基础配置.组间间隔,
            生成位置=基础配置.生成位置
        )
    
@dataclass
class 波次基础配置:
    """波次基础配置"""
    角色平均等级: int
    波次ID: int                 #第几波
    波次体验: 波次体验
    怪物组列表: List[组配置]  
    波次间隔时间: float
    
    

@dataclass
class 波次配置(波次基础配置):
    """波次完整配置"""
    _波战力总值: Optional[float] = None             #缓存机制，是为了访问下面的属性时，让波盈缺换算成英雄和剩余时间计算时，不重复计算
    _波期望战力值: Optional[float] = None
    _波盈缺换算成角色: Optional[float] = None
    _剩余时间: Optional[float] = None

    @property
    def 波战力总值(self) -> float:
        """计算波次总战力值"""
        if self._波战力总值 is None:
            # 计算所有怪物组的战力总和
            self._波战力总值 = sum(组.组战力总值 for 组 in self.怪物组列表)
        return self._波战力总值

    @property
    def 波期望战力值(self) -> float:
        """计算波次期望战力值"""
        if self._波期望战力值 is None:
            print(self.角色平均等级, self.波次ID)
            self._波期望战力值 = tables.Tb阵容战力成长时间分布_2导.get(int(self.角色平均等级 * 100 + self.波次ID)).每波怪物总战力
        return self._波期望战力值

    @property
    def 波盈缺换算成英雄(self) -> float:
        """计算波次盈缺值"""
        if self._波盈缺换算成角色 is None:
            self._波盈缺换算成角色 = (self.波战力总值 - self.波期望战力值) * 全局参数.最大上阵角色数 / tables.Tb阵容战力成长时间分布_2导.get(int(self.角色平均等级 * 100 + self.波次ID)).当前阵容战力
        
        # 检查值是否在有效范围内
        if self._波盈缺换算成角色 > 20 or self._波盈缺换算成角色 < -20:
            错误信息 = f"波盈缺换算成英雄值超出范围：当前值为{self._波盈缺换算成角色}，有效范围为[-20, 20]，请重新调整波次配置"
            raise ValueError(错误信息)
        
        return self._波盈缺换算成角色
    
    @property
    def 剩余时间(self) -> float:
        """计算剩余时间"""
        if self._剩余时间 is None:
            self._剩余时间 = self.波次间隔时间 - sum(组.组内间隔 * 组.数量 for 组 in self.怪物组列表) - sum(组.组间间隔 for 组 in self.怪物组列表)
        
        # 检查值是否在有效范围内
        if self._剩余时间 < 5:
            错误信息 = f"剩余时间值过小：当前值为{self._剩余时间}，最小值应为5，请重新调整波次配置"
            raise ValueError(错误信息)
        
        return self._剩余时间

    @classmethod
    def 从基础配置创建(cls, 基础配置: 波次基础配置) -> '波次配置':
        """从基础配置创建完整配置"""
        return cls(
            角色平均等级=基础配置.角色平均等级,
            波次ID=基础配置.波次ID,
            波次体验=基础配置.波次体验,
            怪物组列表=基础配置.怪物组列表,
            波次间隔时间=基础配置.波次间隔时间,
            _波战力总值=None,
            _波期望战力值=None,
            _波盈缺换算成角色=None,
            _剩余时间=None
        )


