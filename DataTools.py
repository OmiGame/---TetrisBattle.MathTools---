from typing import List, Dict, Any, Union
import random

class 数据工具:
    """数据工具类，提供各种数据处理和生成功能"""
    
    @staticmethod
    def 生成随机整数列表(最小值: int, 最大值: int, 数量: int) -> List[int]:
        """生成指定范围内的随机整数列表
        
        Args:
            最小值: 随机数的最小值
            最大值: 随机数的最大值
            数量: 需要生成的随机数数量
            
        Returns:
            List[int]: 随机整数列表
        """
        return [random.randint(最小值, 最大值) for _ in range(数量)]
    
    @staticmethod
    def 生成随机浮点数列表(最小值: float, 最大值: float, 数量: int, 小数位数: int = 2) -> List[float]:
        """生成指定范围内的随机浮点数列表
        
        Args:
            最小值: 随机数的最小值
            最大值: 随机数的最大值
            数量: 需要生成的随机数数量
            小数位数: 保留的小数位数，默认为2
            
        Returns:
            List[float]: 随机浮点数列表
        """
        return [round(random.uniform(最小值, 最大值), 小数位数) for _ in range(数量)]
    
    @staticmethod
    def 计算列表平均值(数据列表: List[Union[int, float]]) -> float:
        """计算列表的平均值
        
        Args:
            数据列表: 包含数字的列表
            
        Returns:
            float: 列表的平均值
        """
        if not 数据列表:
            return 0.0
        return sum(数据列表) / len(数据列表)
    
    @staticmethod
    def 计算列表标准差(数据列表: List[Union[int, float]]) -> float:
        """计算列表的标准差
        
        Args:
            数据列表: 包含数字的列表
            
        Returns:
            float: 列表的标准差
        """
        if not 数据列表:
            return 0.0
        平均值 = 数据工具.计算列表平均值(数据列表)
        方差 = sum((x - 平均值) ** 2 for x in 数据列表) / len(数据列表)
        return 方差 ** 0.5
    
    @staticmethod
    def 获取列表最大值(数据列表: List[Union[int, float]]) -> Union[int, float]:
        """获取列表中的最大值
        
        Args:
            数据列表: 包含数字的列表
            
        Returns:
            Union[int, float]: 列表中的最大值
        """
        if not 数据列表:
            return 0
        return max(数据列表)
    
    @staticmethod
    def 获取列表最小值(数据列表: List[Union[int, float]]) -> Union[int, float]:
        """获取列表中的最小值
        
        Args:
            数据列表: 包含数字的列表
            
        Returns:
            Union[int, float]: 列表中的最小值
        """
        if not 数据列表:
            return 0
        return min(数据列表)
    
    @staticmethod
    def 列表去重(数据列表: List[Any]) -> List[Any]:
        """去除列表中的重复元素
        
        Args:
            数据列表: 任意类型的列表
            
        Returns:
            List[Any]: 去重后的列表
        """
        return list(set(数据列表))
    
    @staticmethod
    def 列表排序(数据列表: List[Any], 降序: bool = False) -> List[Any]:
        """对列表进行排序
        
        Args:
            数据列表: 任意类型的列表
            降序: 是否按降序排序，默认为False（升序）
            
        Returns:
            List[Any]: 排序后的列表
        """
        return sorted(数据列表, reverse=降序)
    
    @staticmethod
    def 字典按值排序(字典: Dict[Any, Union[int, float]], 降序: bool = False) -> Dict[Any, Union[int, float]]:
        """对字典按值进行排序
        
        Args:
            字典: 键值对字典
            降序: 是否按降序排序，默认为False（升序）
            
        Returns:
            Dict[Any, Union[int, float]]: 排序后的字典
        """
        return dict(sorted(字典.items(), key=lambda x: x[1], reverse=降序)) 