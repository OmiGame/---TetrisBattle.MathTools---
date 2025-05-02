import math
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter
from enum import Enum
from LubanData import tables,全局参数

@dataclass
class 表头信息:
    """表头信息的数据类"""
    显示名称: str
    数据类型: str

    def __post_init__(self):
        """初始化后检查显示名称是否包含特殊符号，因为pyhton的变量名不允许有特殊符号，所以未避免luban导表后出错，显示名称也不能有特殊符号"""
        特殊符号 = "()（）/\\|<>{}[]【】《》"
        for 符号 in 特殊符号:
            if 符号 in self.显示名称:
                raise ValueError(f"表头显示名称 '{self.显示名称}' 不能包含特殊符号 '{符号}'")

class Excel公式参数:
    """管理Excel公式中需要的参数"""
    def __init__(self, ws: Worksheet, 起始行号: int):
        self.ws = ws
        self.起始行号 = 起始行号
        self.最大行号 = 500
        self.怪物波次间隔 = 全局参数.怪物波次间隔  # 这个值应该从全局参数中获取，但为了不引入循环依赖，暂时硬编码

    def 获取公式参数(self) -> Dict[str, Any]:
        """返回Excel公式中需要的所有参数"""
        return {
            "起始行号": self.起始行号,
            "最大行号": self.最大行号,
            "怪物波次间隔": self.怪物波次间隔
        }

@dataclass
class 表格列定义:
    """定义表格列的元数据"""
    列名: str
    列函数: Callable
    参数映射: Dict[str, str]
    excel公式字符串: str = None

    """定义表格列的计算方式， 如果有excel公式字符串，则优先使用excel公式计算，否则使用列函数计算，另外，列函数中不能引用excel的单元格值"""
    def 计算值(self, 实际参数: Dict[str, Any], 工作表: Worksheet = None, 当前行号: int = None, 
             列号映射: Dict[str, int] = None, 起始行号: int = None) -> Any:
        if self.excel公式字符串 and 工作表 and 当前行号 and 列号映射 and 起始行号:
            公式 = self.excel公式字符串
            for 列名, 列号 in 列号映射.items():
                列字母 = get_column_letter(列号)
                公式 = 公式.replace(f"{{{列名}}}", 列字母)
            
            # 获取Excel公式参数
            公式参数 = Excel公式参数(工作表, 起始行号).获取公式参数()
            try:
                公式 = 公式.format(行号=当前行号, **公式参数)
            except KeyError:
                pass
            return 公式
        return self.列函数(实际参数)

class 表头枚举基类(Enum):
    """表头枚举的基类，提供更便捷的访问方式，__str__是返回预定义的字符串，str(obj)会调用此方法"""
    def __str__(self):
        return self.value.显示名称
    
    @property
    def 类型(self):
        return self.value.数据类型

class 角色成长表:
    """角色成长表的数据定义类"""
    # 表格基本信息
    表格名称: str = "#角色成长数据.xlsx"
    默认工作表名称: str = "某角色成长"
    
    class 表头(表头枚举基类):
        """角色成长表的表头枚举"""
        角色名称 = 表头信息("角色名称", "string")
        等级 = 表头信息("等级", "int")
        血量 = 表头信息("血量", "float")
        攻击力 = 表头信息("攻击力", "float")
        攻击速度_S = 表头信息("攻击速度_S", "float")
        攻击范围_格 = 表头信息("攻击范围_格", "float")
        移速_格_S = 表头信息("移速_格_S", "float")
        基础DPS = 表头信息("基础DPS", "float")
        血量战力 = 表头信息("血量战力", "float")
        DPS战力 = 表头信息("DPS战力", "float")
        血量特效战力 = 表头信息("血量特效战力", "float")
        DPS特效战力 = 表头信息("DPS特效战力", "float")
        基础总战力 = 表头信息("基础总战力", "float")
        解锁技能数 = 表头信息("解锁技能数", "int")
        技能列表 = 表头信息("技能列表", "string")
        技能解锁后的总战力 = 表头信息("技能解锁后的总战力", "float")

        @classmethod
        def 获取表头字典(cls) -> Dict[str, str]:
            return {str(成员): 成员.类型 for 成员 in cls}

    # 表格其他属性
    行数据类型: str = "等级"
    行数据起始值: int = 1
    行数据结束值: int = 100
    技能列表列号: int = 15

    # 使用枚举获取表头
    headers = 表头.获取表头字典()

    @classmethod
    def 获取行数据范围(cls) -> tuple[int, int]:
        """实际数据的范围，不包括表头
        可以根据需要重写此方法，返回自定义的行数据范围
        
        Returns:
            tuple[int, int]: (起始值, 结束值)
        """
        from LubanData import 全局参数
        return (cls.行数据起始值, 全局参数.角色等级上限)

    @classmethod
    def 获取行数据(cls, 当前值: int) -> str:
        """获取行数据的显示值
        可以根据需要重写此方法，返回自定义的行数据显示值
        
        Args:
            当前值: 当前的行数据值
            
        Returns:
            str: 行数据的显示值
        """
        return f"{cls.行数据类型}{当前值}"

    @classmethod
    def 获取列函数映射(cls) -> Dict[int, 表格列定义]:
        from BattleFormula import 战斗公式
        from ExcelTools import 表格工具
        
        return {
            1: 表格列定义(
                str(cls.表头.角色名称),
                lambda params: f'{params["角色名称"]},{params["角色等级"]}',
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            2: 表格列定义(
                str(cls.表头.等级),
                lambda params: params["角色等级"],
                {"角色等级": "角色等级"}
            ),
            3: 表格列定义(
                str(cls.表头.血量),
                lambda params: 战斗公式.计算基础血量(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            4: 表格列定义(
                str(cls.表头.攻击力),
                lambda params: 战斗公式.计算基础攻击力(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            5: 表格列定义(
                str(cls.表头.攻击速度_S),
                lambda params: 战斗公式.计算基础攻速(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            6: 表格列定义(
                str(cls.表头.攻击范围_格),
                lambda params: 战斗公式.计算基础攻击范围(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            7: 表格列定义(
                str(cls.表头.移速_格_S),
                lambda params: 战斗公式.计算基础移速(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            8: 表格列定义(
                str(cls.表头.基础DPS),
                lambda params: 战斗公式.计算基础DPS(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            9: 表格列定义(
                str(cls.表头.血量战力),
                lambda params: 战斗公式.计算基础血量战力(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            10: 表格列定义(
                str(cls.表头.DPS战力),
                lambda params: 战斗公式.计算基础DPS战力(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            11: 表格列定义(
                str(cls.表头.血量特效战力),
                lambda params: 战斗公式.计算基础血量特效战力(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            12: 表格列定义(
                str(cls.表头.DPS特效战力),
                lambda params: 战斗公式.计算基础DPS特效战力(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            13: 表格列定义(
                str(cls.表头.基础总战力),
                lambda params: 战斗公式.计算基础总战力(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            14: 表格列定义(
                str(cls.表头.解锁技能数),
                lambda params: 战斗公式.计算解锁技能数(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            ),
            15: 表格列定义(
                str(cls.表头.技能列表),
                lambda params: 表格工具.列表元素字符串拼接(
                    params["列表"], params["分隔符"]
                ),
                {
                    "列表": "列表",
                    "分隔符": "分隔符"
                }
            ),
            16: 表格列定义(
                str(cls.表头.技能解锁后的总战力),
                lambda params: 战斗公式.计算解锁技能的总战力(params["角色名称"], params["角色等级"]),
                {"角色名称": "角色名称", "角色等级": "角色等级"}
            )
        }

    #主要功能是获取实际键。因为实际键需要更多的数据，这些数据只有通过函数传入。
    @classmethod
    def 创建行参数(cls, ws: Worksheet, 角色名称: str, 角色等级: int, 行号: int) -> Dict[str, Any]:
        """创建行参数字典
        为每一行数据创建通用的参数字典，包含所有列可能需要的参数
        
        Args:
            ws: 工作表对象
            角色名称: 其实是传入的sheet名，ws.titile
            角色等级: 当前行数据值
            行号: 当前处理的行号
        """
        from BattleFormula import 战斗公式
        
        return {
            "角色名称": 角色名称,
            "角色等级": 角色等级,
            "列表": 战斗公式.计算已解锁技能名称列表(角色名称, 角色等级),
            "分隔符": ",",
        } 

class 阵容战力成长表:
    """阵容战力成长表的数据定义类"""
    # 表格基本信息
    表格名称: str = "#阵容战力成长表.xlsx"
    默认工作表名称: str = "某角色成长"
    
    class 表头(表头枚举基类):
        """阵容战力成长表的表头枚举"""
        阵容组合名称 = 表头信息("阵容组合名称", "string")
        平均等级 = 表头信息("平均等级", "int")
        初始战力 = 表头信息("初始战力", "float")
        终点战力 = 表头信息("终点战力", "float")
        终点战力产出效率 = 表头信息("终点战力产出效率", "float")

        @classmethod
        def 获取表头字典(cls) -> Dict[str, str]:
            return {str(成员): 成员.类型 for 成员 in cls}

    # 表格其他属性
    行数据类型: str = "等级"
    行数据起始值: int = 1
    行数据结束值: int = 100
    标准阵容列表: List[str] = ["弓箭手", "士兵","弓"]
    测试阵容列表: List[str] = ["士兵","弓箭手"]

    # 使用枚举获取表头
    headers = 表头.获取表头字典()

    @classmethod
    def 获取行数据范围(cls) -> tuple[int, int]:
        """实际数据的范围，不包括表头
        可以根据需要重写此方法，返回自定义的行数据范围
        
        Returns:
            tuple[int, int]: (起始值, 结束值)
        """
        from LubanData import 全局参数
        return (cls.行数据起始值, 全局参数.角色等级上限)

    @classmethod
    def 获取行数据(cls, 当前值: int) -> str:
        """获取行数据的显示值
        可以根据需要重写此方法，返回自定义的行数据显示值
        
        Args:
            当前值: 当前的行数据值
            
        Returns:
            str: 行数据的显示值
        """
        return f"{cls.行数据类型}{当前值}"

    @classmethod
    def 获取列函数映射(cls) -> Dict[int, 表格列定义]:
        from BattleFormula import 战斗公式
        from ExcelTools import 表格工具
        
        return {
            1: 表格列定义(
                str(cls.表头.阵容组合名称),
                lambda params: f'{表格工具.列表元素字符串拼接(params["阵容组合列表"])},{params["角色平均等级"]}',
                {"阵容组合列表": "阵容组合列表","角色平均等级": "角色平均等级"}
            ),
            2: 表格列定义(
                str(cls.表头.平均等级),
                lambda params: params["角色平均等级"],
                {"角色平均等级": "角色平均等级"}
            ),
            3: 表格列定义(
                str(cls.表头.初始战力),
                lambda params: 战斗公式.计算角色阵容的初始战力(params["阵容字典"]),
                {"阵容字典": "阵容字典"}
            ),
            4: 表格列定义(
                str(cls.表头.终点战力),
                lambda params: 战斗公式.计算阵容选择多次平均肉鸽技能后的战力(params["阵容组合列表"], params["角色平均等级"], params["选择次数"]),
                {"阵容组合列表": "阵容组合列表", "角色平均等级": "角色平均等级", "选择次数": "选择次数"}
            ),
            5: 表格列定义(
                str(cls.表头.终点战力产出效率),
                lambda params: 战斗公式.计算平均战力产出效率(params["阵容组合列表"], params["角色平均等级"], params["选择次数"]),
                {"阵容组合列表": "阵容组合列表", "角色平均等级": "角色平均等级", "选择次数": "选择次数"}
            )
        }

    #主要功能是获取实际键。因为实际键需要更多的数据，这些数据只有通过函数传入。
    @classmethod
    def 创建行参数(cls, ws: Worksheet, 阵容组合名称: str, 平均等级: int, 行号: int) -> Dict[str, Any]:
        """创建行参数字典
        为每一行数据创建通用的参数字典，包含所有列可能需要的参数
        
        Args:
            ws: 工作表对象
            角色名称: 其实是传入的sheet名，ws.titile
            角色等级: 当前行数据值
            行号: 当前处理的行号
            
        Returns:
            Dict[str, Any]: 包含所有可能需要的参数的字典
        """
        from ExcelTools import 表格工具
        from LubanData import 全局参数
        return {
            "阵容组合列表": 表格工具.找到类字段(cls, 阵容组合名称),
            "角色平均等级": 平均等级,
            "阵容字典": {角色名:平均等级 for 角色名 in 表格工具.找到类字段(cls, 阵容组合名称)},
            "选择次数": 全局参数.肉鸽技能选择次数,
        } 

class 肉鸽技能节奏:
    """肉鸽技能节奏表的数据定义类"""
    # 表格基本信息
    表格名称: str = "#肉鸽技能选择节奏.xlsx"
    默认工作表名称: str = "肉鸽技能选择节奏"
    
    class 表头(表头枚举基类):
        """肉鸽技能节奏表的表头枚举"""
        肉鸽技能升级次数 = 表头信息("肉鸽技能升级次数", "int")
        理论所需经验值 = 表头信息("理论所需经验值", "float")
        玩家消除行数 = 表头信息("玩家消除行数", "int")
        玩家获得的经验总值 = 表头信息("玩家获得的经验总值", "int")
        获得经验的时间_s = 表头信息("获得经验的时间_s", "float")
        时间取整每30s = 表头信息("时间取整每30s", "int")
        根据时间计数 = 表头信息("根据时间计数", "int")
        怪物波次模拟 = 表头信息("怪物波次模拟","int")
        选择技能次数 = 表头信息("选择技能次数","int")
        总次数 = 表头信息("总次数","int")

        @classmethod
        def 获取表头字典(cls) -> Dict[str, str]:
            return {str(成员): 成员.类型 for 成员 in cls}

    # 表格其他属性
    行数据类型: str = "选择次数"
    行数据起始值: int = 1
    行数据结束值: int = 100

    # 使用枚举获取表头
    headers = 表头.获取表头字典()

    @classmethod
    def 获取行数据范围(cls) -> tuple[int, int]:
        """实际数据的范围，不包括表头
        可以根据需要重写此方法，返回自定义的行数据范围
        
        Returns:
            tuple[int, int]: (起始值, 结束值)
        """
        from LubanData import 全局参数
        return (cls.行数据起始值, 全局参数.肉鸽技能选择次数+ 10 )

    @classmethod
    def 获取行数据(cls, 当前值: int) -> str:
        """获取行数据的显示值
        可以根据需要重写此方法，返回自定义的行数据显示值
        Args:
            当前值: 当前的行数据值
        Returns:
            str: 行数据的显示值
        """
        return f"{cls.行数据类型}{当前值}"

    @classmethod
    def 获取列函数映射(cls) -> Dict[int, 表格列定义]:
        from BattleFormula import 战斗公式
        from LubanData import 全局参数
        
        return {
            1: 表格列定义(
                str(cls.表头.肉鸽技能升级次数),
                lambda params: params["肉鸽技能升级次数"],
                {"肉鸽技能升级次数": "肉鸽技能升级次数"}
            ),
            2: 表格列定义(
                str(cls.表头.理论所需经验值),
                lambda params: 战斗公式.计算肉鸽技能经验值(params["肉鸽技能升级次数"]),
                {"肉鸽技能升级次数": "肉鸽技能升级次数"}
            ),
            3: 表格列定义(
                str(cls.表头.玩家消除行数),
                lambda params: math.ceil(战斗公式.计算肉鸽技能经验值(params["肉鸽技能升级次数"])/全局参数.每行经验值),
                {"肉鸽技能升级次数": "肉鸽技能升级次数"}
            ),
            4: 表格列定义(
                str(cls.表头.玩家获得的经验总值),
                lambda params: 战斗公式.计算经验总值(params["肉鸽技能升级次数"]),
                {"肉鸽技能升级次数": "肉鸽技能升级次数"}
            ),
            5: 表格列定义(
                str(cls.表头.获得经验的时间_s),
                lambda params: 战斗公式.计算经验总值(params["肉鸽技能升级次数"])/全局参数.玩家每秒获取经验速度,
                {"肉鸽技能升级次数": "肉鸽技能升级次数"}
            ),
            6: 表格列定义(
                str(cls.表头.时间取整每30s),
                None,  
                {},  
                "=ROUNDUP({获得经验的时间_s}{行号}/30,0)"  
            ),
            7: 表格列定义(
                str(cls.表头.根据时间计数),
                None,
                {},
                "=COUNTIF(${时间取整每30s}${起始行号}:${时间取整每30s}{行号},${时间取整每30s}{行号})" 
            ),
            8: 表格列定义(
                str(cls.表头.怪物波次模拟),
                lambda params :params["肉鸽技能升级次数"],
                {"肉鸽技能升级次数": "肉鸽技能升级次数"},
            ),
            9: 表格列定义(
                str(cls.表头.选择技能次数),
                None,
                {},
                "=IFERROR(LOOKUP(2,1/(${时间取整每30s}${起始行号}:${时间取整每30s}{最大行号} = {怪物波次模拟}{行号}),${根据时间计数}${起始行号}:${根据时间计数}{最大行号}),0)"
            ),
            10: 表格列定义(
                str(cls.表头.总次数),
                None,
                {},
                "=SUM(${选择技能次数}${起始行号}:${选择技能次数}{行号})"  
            )
        }

    #主要功能是获取实际键。因为实际键需要更多的数据，这些数据只有通过函数传入。
    @classmethod
    def 创建行参数(cls, ws: Worksheet, sheet_name: str, 数据行当前值: int, 行号: int) -> Dict[str, Any]:
        """创建行参数字典
        为每一行数据创建通用的参数字典，包含所有列可能需要的参数
        ws: 工作表对象
            角色名称: 其实是传入的sheet名，ws.titile
            角色等级: 当前行数据值
            行号: 当前处理的行号
        """
        return {
            "肉鸽技能升级次数": 数据行当前值
        } 
    
class 阵容战力成长时间分布:
    """阵容战力成长的时间分布表"""
    # 表格基本信息
    表格名称: str = "#阵容战力成长时间分布.xlsx"
    默认工作表名称: str = "等级X"
    
    class 表头(表头枚举基类):
        """阵容战力成长时间分布的表头枚举"""
        怪物波次 = 表头信息("怪物波次", "int")
        时间点 = 表头信息("时间点_30s", "float")
        阵容 = 表头信息("阵容", "string")
        选技能次数 = 表头信息("选技能次数", "int")
        总次数 = 表头信息("总次数", "int")
        消除倍率 = 表头信息("消除倍率", "float")
        每块小兵增加期望值 = 表头信息("每块小兵增加期望值", "float")
        初始战力 = 表头信息("初始战力", "float")
        当前阵容战力 = 表头信息("当前阵容战力", "float")
        战力产出效率 = 表头信息("战力产出效率", "float")
        每波怪物总战力 = 表头信息("每波怪物总战力", "float")
        平均相当于多少个上阵角色 = 表头信息("平均相当于多少个上阵角色", "float")

        @classmethod
        def 获取表头字典(cls) -> Dict[str, str]:
            return {str(成员): 成员.类型 for 成员 in cls}

    # 表格其他属性
    行数据类型: str = "波次"
    行数据起始值: int = 1
    行数据结束值: int = 100
    标准阵容列表: List[str] = ["弓箭手", "士兵","弓"]
    测试阵容列表: List[str] = ["士兵","弓箭手"]

    # 使用枚举获取表头
    headers = 表头.获取表头字典()

    @classmethod
    def 获取行数据范围(cls) -> tuple[int, int]:
        """实际数据的范围，不包括表头
        可以根据需要重写此方法，返回自定义的行数据范围
        
        Returns:
            tuple[int, int]: (起始值, 结束值)
        """
        from LubanData import 全局参数
        return (cls.行数据起始值, 全局参数.角色等级上限)

    @classmethod
    def 获取行数据(cls, 当前值: int) -> str:
        """获取行数据的显示值
        可以根据需要重写此方法，返回自定义的行数据显示值
        
        Args:
            当前值: 当前的行数据值
            
        Returns:
            str: 行数据的显示值
        """
        return f"{cls.行数据类型}{当前值}"

    @classmethod
    def 获取列函数映射(cls) -> Dict[int, 表格列定义]:
        from BattleFormula import 战斗公式
        return {
            1: 表格列定义(
                str(cls.表头.怪物波次),
                lambda params: params["怪物波次"],
                {"怪物波次": "怪物波次"}
            ),
            2: 表格列定义(
                str(cls.表头.时间点),
                lambda params: params["时间点"],
                {"时间点": "时间点"}
            ),
            3: 表格列定义(
                str(cls.表头.阵容),
                lambda params: params["阵容列表"],
                {"阵容列表": "阵容列表"}
            ),
            4: 表格列定义(
                str(cls.表头.选技能次数),
                lambda params: params["选技能次数"],
                {"选技能次数": "选技能次数"}
            ),
            5: 表格列定义(
                str(cls.表头.总次数),
                None,
                {},
                "=SUM(${选技能次数}${起始行号}:${选技能次数}{行号})"  
            ),
            6: 表格列定义(
                str(cls.表头.消除倍率),
                lambda params: 战斗公式.获取平均消除倍率加成() ** params["总次数"],
                {"总次数": "总次数"}
            ),
            7: 表格列定义(
                str(cls.表头.每块小兵增加期望值),
                lambda params: 战斗公式.获取平均每块小兵增加期望值加成() * params["总次数"],
                {"总次数": "总次数"}
            ),
            8: 表格列定义(
                str(cls.表头.初始战力),
                lambda params: 战斗公式.计算角色阵容的初始战力(params["阵容字典"]),
                {"阵容字典": "阵容字典"}
            ),
            9: 表格列定义(
                str(cls.表头.当前阵容战力),
                lambda params: 战斗公式.计算阵容选择多次平均肉鸽技能后的战力(params["阵容列表"], params["角色平均等级"], params["总次数"]),
                {"阵容列表": "阵容列表", "角色平均等级": "角色平均等级", "总次数": "总次数"}
            ),
            10: 表格列定义(
                str(cls.表头.战力产出效率),
                lambda params: 战斗公式.计算平均战力产出效率(params["阵容列表"], params["角色平均等级"], params["总次数"]),
                {"阵容列表": "阵容列表", "角色平均等级": "角色平均等级", "总次数": "总次数"}
            ),
            11: 表格列定义(
                str(cls.表头.每波怪物总战力),
                None,
                {},
                "=${战力产出效率}${行号}*{怪物波次间隔}"  # 使用公式参数中的怪物波次间隔
            ),
            12: 表格列定义(
                str(cls.表头.平均相当于多少个上阵角色),
                None,
                {},
                "=${每波怪物总战力}${行号}/(${当前阵容战力}${行号}/4)"
            )
        }

    #主要功能是获取实际键。因为实际键需要更多的数据，这些数据只有通过函数传入。
    @classmethod
    def 创建行参数(cls, ws: Worksheet, 等级X: str, 怪物波次: int, 行号: int) -> Dict[str, Any]:
        """创建行参数字典
        为每一行数据创建通用的参数字典，包含所有列可能需要的参数
        
        Args:
            ws: 工作表对象
            第二个参数: 其实是传入的sheet名，ws.titile
            第三个参数: 当前行数据值
            行号: 当前处理的行号
            
        Returns:
            Dict[str, Any]: 包含所有可能需要的参数的字典
        """
        from LubanData import 全局参数
        return {
            "怪物波次": 怪物波次,
            "时间点": 怪物波次 * 全局参数.怪物波次间隔,
            "阵容列表": cls.标准阵容列表,
            "选技能次数": tables.Tb肉鸽技能选择节奏.get(怪物波次).选择技能次数,
            "角色平均等级": int(等级X.replace("等级", "")),
            "总次数": tables.Tb肉鸽技能选择节奏.get(怪物波次).总次数,
            "阵容字典": {角色名:int(等级X.replace("等级", "")) for 角色名 in cls.标准阵容列表},
        }


