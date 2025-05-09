"""关卡数据类型"""
from dataclasses import dataclass
from enum import Enum
from ..WaveData.WaveDataType import 波次配置

class 难度类型(Enum):
    """难度类型"""
    轻松 = "轻松"
    一般 = "一般"
    困难 = "困难"
    地狱 = "地狱"


@dataclass
class 关卡基础配置:
    """关卡基础配置"""
    关卡ID: int
    生成延迟时间: float             #秒
    难度类型: 难度类型
    我方城堡血量: int
    敌方城堡血量: int
    限时生成时长: float = None      #分钟
    三星达成百分比:float = None     #城堡剩余血量
    二星达成百分比:float = None     #城堡剩余血量
    一星达成百分比:float = None     #城堡剩余血量
    角色平均等级参考: int
    波次配置: list[波次配置]

    
