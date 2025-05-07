import json
import os
from typing import Dict, List
from MonsterData.MonsterTypes import 怪物基础属性数据, 怪物职业

class 已生成怪物:
    """管理所有已生成的怪物数据，使用单例模式确保只有一个实例"""
    _instance = None
    _怪物数据字典: Dict[str, 怪物基础属性数据] = {}
    _数据目录 = "MonsterData"
    _怪物数据文件路径 = os.path.join(_数据目录, "怪物数据.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(已生成怪物, cls).__new__(cls)
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
                "属性数据": 怪物.各等级属性数据,
                "基础攻击速度": 怪物.基础攻击速度,
                "基础攻击范围": 怪物.基础攻击范围,
                "基础移动速度": 怪物.基础移动速度,
                "血量特效倍率": 怪物.血量特效倍率,
                "DPS特效倍率": 怪物.DPS特效倍率
            }
        
        with open(cls._怪物数据文件路径, 'w', encoding='utf-8') as f:
            json.dump(数据字典, f, ensure_ascii=False, indent=4)

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
    def 添加怪物(cls, 怪物: 怪物基础属性数据) -> None:
        """添加一个怪物到数据字典中
        
        Args:
            怪物: 要添加的怪物基础属性数据
        """
        cls._怪物数据字典[怪物.名称] = 怪物
        cls._保存数据()  # 保存到文件
        print(f"已添加怪物到怪物数据字典: {怪物.名称}")

    @classmethod
    def 获取怪物(cls, 怪物名称: str) -> 怪物基础属性数据:
        """获取指定名称的怪物数据
        
        Args:
            怪物名称: 要获取的怪物名称
            
        Returns:
            怪物基础属性数据: 对应的怪物数据
            
        Raises:
            KeyError: 如果找不到指定名称的怪物
        """
        if 怪物名称 not in cls._怪物数据字典:
            raise KeyError(f"找不到名为 {怪物名称} 的怪物数据")
        return cls._怪物数据字典[怪物名称]

    @classmethod
    def 获取所有怪物(cls) -> Dict[str, 怪物基础属性数据]:
        """获取所有已生成的怪物数据
        
        Returns:
            Dict[str, 怪物基础属性数据]: 所有怪物数据的字典
        """
        return cls._怪物数据字典.copy()

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
    def 清空数据(cls) -> None:
        """清空所有已生成的怪物数据"""
        cls._怪物数据字典.clear()
        if os.path.exists(cls._怪物数据文件路径):
            os.remove(cls._怪物数据文件路径) 