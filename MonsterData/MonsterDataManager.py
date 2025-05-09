"""怪物数据管理器，负责保存和加载怪物数据"""
import json
import os
from typing import Dict, List
from MonsterData.MonsterTypes import 怪物基础属性数据, 怪物职业, 已设计怪物, 怪物品质

class 怪物数据保存器:
    """已生成的怪物数据管理类"""
    _instance = None
    _怪物数据字典: Dict[str, 怪物基础属性数据] = {}
    _数据目录 = "MonsterData"
    _怪物数据文件路径 = os.path.join(_数据目录, "怪物数据.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(怪物数据保存器, cls).__new__(cls)
            # 确保数据目录存在
            if not os.path.exists(cls._数据目录):
                os.makedirs(cls._数据目录)
            # 尝试从文件加载数据
            cls._加载数据()
        return cls._instance

    @classmethod
    def _保存数据(cls) -> None:
        """将怪物数据保存到文件"""
        # 确保数据目录存在
        if not os.path.exists(cls._数据目录):
            os.makedirs(cls._数据目录)
            
        数据字典 = {}
        for 名称, 怪物 in cls._怪物数据字典.items():
            数据字典[名称] = {
                "名称": 怪物.名称,
                "职业": 怪物.职业.value,
                "品质": 怪物.品质.value,
                "属性数据": 怪物.各等级属性数据,
                "基础攻击速度": 怪物.基础攻击速度,
                "基础攻击范围": 怪物.基础攻击范围,
                "基础移动速度": 怪物.基础移动速度,
                "血量特效倍率": 怪物.血量特效倍率,
                "DPS特效倍率": 怪物.DPS特效倍率
            }
        
        with open(cls._怪物数据文件路径, 'w', encoding='utf-8') as f:
            json.dump(数据字典, f, ensure_ascii=False, indent=4)
        print(f"已保存怪物数据到文件: {cls._怪物数据文件路径}")

    @classmethod
    def _加载数据(cls) -> None:
        """从文件加载怪物数据"""
        if not os.path.exists(cls._怪物数据文件路径):
            print(f"怪物数据文件不存在: {cls._怪物数据文件路径}")
            return
        
        try:
            with open(cls._怪物数据文件路径, 'r', encoding='utf-8') as f:
                数据字典 = json.load(f)
            
            print(f"正在加载怪物数据，找到 {len(数据字典)} 个怪物")
            for 名称, 数据 in 数据字典.items():
                print(f"加载怪物: {名称}")
                怪物 = 怪物基础属性数据(
                    名称=数据["名称"],
                    职业=怪物职业(数据["职业"]),
                    品质=怪物品质(数据["品质"]),
                    各等级属性数据=数据["属性数据"],
                    基础攻击速度=数据["基础攻击速度"],
                    基础攻击范围=数据["基础攻击范围"],
                    基础移动速度=数据["基础移动速度"],
                    血量特效倍率=数据["血量特效倍率"],
                    DPS特效倍率=数据["DPS特效倍率"]
                )
                cls._怪物数据字典[名称] = 怪物
            print(f"已加载的怪物列表: {list(cls._怪物数据字典.keys())}")
        except Exception as e:
            print(f"加载怪物数据时出错: {e}")

    @classmethod
    def 添加怪物(cls, 怪物数据: 怪物基础属性数据):
        """添加一个怪物数据到保存器中"""
        cls._怪物数据字典[怪物数据.名称] = 怪物数据

    @classmethod
    def 获取怪物(cls, 怪物名称: str) -> 怪物基础属性数据:
        """获取指定名称的怪物数据"""
        if 怪物名称 not in cls._怪物数据字典:
            raise KeyError(f"找不到名为 {怪物名称} 的怪物数据")
        return cls._怪物数据字典[怪物名称]

    @classmethod
    def 获取所有怪物(cls) -> List[怪物基础属性数据]:
        """获取所有保存的怪物数据"""
        return list(cls._怪物数据字典.values())

    @classmethod
    def 清空数据(cls):
        """清空所有保存的怪物数据"""
        cls._怪物数据字典.clear()

    @classmethod
    def 获取所有怪物名称(cls) -> List[str]:
        """获取所有已生成怪物的名称列表
        
        Returns:
            List[str]: 怪物名称列表
        """
        return list(cls._怪物数据字典.keys())

    @classmethod
    def 按职业筛选怪物(cls, 职业: 怪物职业) -> Dict[str, 怪物基础属性数据]:
        """按职业筛选怪物数据
        
        Args:
            职业: 要筛选的怪物职业
            
        Returns:
            Dict[str, 怪物基础属性数据]: 符合职业要求的怪物数据字典
        """
        return {
            名称: 怪物 for 名称, 怪物 in cls._怪物数据字典.items()
            if 怪物.职业 == 职业
        }

    @classmethod
    def 按职业获取怪物名称(cls, 职业: 怪物职业) -> List[str]:
        """按职业获取怪物名称列表
        
        Args:
            职业: 要筛选的怪物职业
            
        Returns:
            List[str]: 符合职业要求的怪物名称列表
        """
        return [
            名称 for 名称, 怪物 in cls._怪物数据字典.items()
            if 怪物.职业 == 职业
        ]

    @classmethod
    def 添加所有怪物(cls, 怪物数据列表: List[怪物基础属性数据]):
        """批量添加怪物数据到保存器中"""
        for 怪物数据 in 怪物数据列表:
            cls.添加怪物(怪物数据)