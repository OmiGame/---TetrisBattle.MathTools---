"""计算阵容强度的方法"""
import math
# from LubanData import 全局参数
import numpy as np
from itertools import combinations_with_replacement
from EconomySystem.EcoDataType import 阵容强度数据, 角色碎片数据, 关卡阶段枚举
from EconomySystem.CharacterFrag import 角色碎片计算, 全局参数

# 创建模拟的全局参数类，用于测试
class 全局参数:
    """模拟的全局参数类，用于测试"""
    角色等级上限 = 20
    最大上阵角色数 = 3
    角色品质划分 = 3

class 阵容强度计算:
    # 从阵容强度数据类引用数据
    角色品质 = 阵容强度数据.角色品质
    同等级的角色品质强度 = 阵容强度数据.同等级的角色品质强度
    角色品质成长倍率 = 阵容强度数据.角色品质成长倍率
    

    @classmethod
    def 生成所有阵容(cls,角色品质:list[str]):
        """生成所有允许重复的无序阵容组合"""
        等级列表 = list(range(1, 全局参数.角色等级上限 + 1))  # 假设等级1~20
        最大上阵角色数 = 全局参数.最大上阵角色数
        
        # 生成所有角色（品质+等级）的可能个体
        所有角色 = [(品质, 等级) for 品质 in 角色品质 for 等级 in 等级列表]
        
        # 生成所有无序阵容组合（允许重复）
        所有阵容 = list(combinations_with_replacement(所有角色, 最大上阵角色数))
        
        return 所有阵容

    @classmethod
    def 计算角色强度(cls,品质:str,等级:int) -> float:
        """计算角色强度"""
        return cls.同等级的角色品质强度[品质] * (cls.角色品质成长倍率[品质]**(等级-1))
    

    @classmethod
    def 计算达到目标强度时各品质角色的最低等级(cls, 目标强度:float):
        """
        计算达到目标强度时各品质角色的最低等级
        :return: 字典，包含各品质角色所需的最低等级（如不能达到则为0）
        """
        # 同等级基础强度
        base_strength = 阵容强度计算.同等级的角色品质强度
        
        # 各品质成长倍率
        growth_rate = 阵容强度计算.角色品质成长倍率
        
        result = {}
        
        for quality in 阵容强度计算.角色品质:
            if 目标强度 <= 0:
                result[quality] = 0
                continue
                
            # 计算所需等级
            if base_strength[quality] * growth_rate[quality]**(全局参数.角色等级上限-1) < 目标强度:
                # 即使满级也无法达到目标强度
                result[quality] = 0
            else:
                # 计算最小等级
                min_level = math.ceil(math.log(目标强度 / base_strength[quality], growth_rate[quality])) + 1
                # 确保等级在合理范围内
                min_level = max(1, min(min_level, 全局参数.角色等级上限))
                result[quality] = min_level
        
        return result

    @classmethod
    def 计算阵容强度(cls,角色阵容品质等级: list[tuple[str,int]]) -> float:
        """计算阵容强度"""
        return sum([cls.计算角色强度(品质,等级) for 品质,等级 in 角色阵容品质等级])
    
    
    @classmethod
    def 计算阵容强度范围(cls) -> tuple[float,float]:
        """计算阵容强度范围"""
        最低品质 = min(cls.同等级的角色品质强度, key=lambda k: cls.同等级的角色品质强度[k])
        最高品质 = max(cls.同等级的角色品质强度, key=lambda k: cls.同等级的角色品质强度[k])
        最低等级 = 1
        最高等级 = 全局参数.角色等级上限
        最差阵容 = [(最低品质,最低等级)] * 全局参数.最大上阵角色数
        最优阵容 = [(最高品质,最高等级)] * 全局参数.最大上阵角色数

        return cls.计算阵容强度(最差阵容),cls.计算阵容强度(最优阵容)
    
    @classmethod
    def 计算所有组合数(cls) -> int:
        """计算允许重复的无序阵容组合数"""
        N = 全局参数.角色等级上限
        k = 全局参数.最大上阵角色数
        return math.comb(3 * N + k - 1, k)
    
    @classmethod
    def 计算强度步长(cls) -> float:
        """计算强度提升的基本单位"""
        组合数 = cls.计算所有组合数()
        最差强度, 最优强度 = cls.计算阵容强度范围()
        return (最优强度 - 最差强度) / (组合数 - 1)
    
    # 初始化角色强度表和排序后的角色列表
    @classmethod
    def 初始化角色强度表(cls):
        """初始化角色强度表"""
        角色强度表 = {}
        for 品质 in cls.角色品质:
            for 等级 in range(1, 全局参数.角色等级上限 + 1):
                角色强度表[(品质, 等级)] = cls.计算角色强度(品质, 等级)
        return 角色强度表
    
    @classmethod
    def 初始化排序后的角色(cls):
        """初始化排序后的角色列表"""
        return sorted(cls.角色强度表.keys(), key=lambda x: cls.角色强度表[x])
    
    # 使用类方法初始化类变量
    角色强度表 = {}  # 先定义一个空字典
    排序后的角色 = []  # 先定义一个空列表

    @classmethod
    def 计算最低适配阵容(cls, 目标强度: float) -> list[tuple[str, int]]:
        """动态规划 + 二分查找"""
        """
        预处理排序
            将所有角色按强度排序后，可以用二分查找直接定位到目标强度附近。
        动态填充
            用 [中位角色] * k 快速生成候选阵容，避免逐角色计算。
        滑动窗口微调
            从右向左替换角色，确保每次替换都是当前最弱的可行选择。
        """
        # 特殊情况处理
        if 目标强度 <= cls.计算阵容强度([("绿色", 1)] * 全局参数.最大上阵角色数):
            print(f"目标强度低于最小强度{cls.计算阵容强度([('绿色', 1)] * 全局参数.最大上阵角色数)}")
            return [("绿色", 1)] * 全局参数.最大上阵角色数
        if 目标强度 > cls.计算阵容强度([("紫色", 全局参数.角色等级上限)] * 全局参数.最大上阵角色数):
            print(f"目标强度超出最大强度{cls.计算阵容强度([('紫色', 全局参数.角色等级上限)] * 全局参数.最大上阵角色数)}")
            return None

        # 关键优化：二分查找最弱角色组合
        left, right = 0, len(cls.排序后的角色) - 1
        best_combination = None
        
        while left <= right:
            mid = (left + right) // 2
            candidate = [cls.排序后的角色[mid]] * 全局参数.最大上阵角色数
            candidate_strength = sum(cls.角色强度表[role] for role in candidate)
            
            if candidate_strength >= 目标强度:
                best_combination = candidate
                right = mid - 1  # 尝试更弱的角色
            else:
                left = mid + 1
        
        # 最终微调（确保刚好满足）
        if best_combination:
            return cls.微调阵容(best_combination, 目标强度)
        return None
    
    @classmethod
    def 微调阵容(cls, squad: list[tuple[str, int]], target: float) -> list[tuple[str, int]]:
        """用滑动窗口微调，确保强度刚好≥target且最弱"""
        current_strength = sum(cls.角色强度表[role] for role in squad)
        
        # 从右向左尝试替换更弱的角色
        for i in reversed(range(len(squad))):
            current_role = squad[i]
            current_role_strength = cls.角色强度表[current_role]
            
            # 在排序表中找比当前角色稍弱的下一个角色
            idx = cls.排序后的角色.index(current_role)
            if idx == 0:
                continue  # 已经是最弱角色
            
            for j in range(idx - 1, -1, -1):
                weaker_role = cls.排序后的角色[j]
                new_strength = current_strength - current_role_strength + cls.角色强度表[weaker_role]
                
                if new_strength >= target:
                    squad[i] = weaker_role
                    current_strength = new_strength
                    break
                else:
                    break  # 继续尝试下一个位置
        return squad
    
    @classmethod
    def 分配关卡阵容(cls, 所有阵容, 关卡数=100, 最大阵容强度百分比=0.8):
        # 按强度排序所有阵容
        所有阵容.sort(key=lambda x: cls.计算阵容强度(x))
        
        # 获取强度范围
        最小强度 = cls.计算阵容强度(所有阵容[0])
        最大强度 = cls.计算阵容强度(所有阵容[-1]) * 最大阵容强度百分比
        强度范围 = 最大强度 - 最小强度
        
        # 计算每个关卡的目标强度（线性分布）
        目标强度列表 = [最小强度 + (强度范围 * i / (关卡数 - 1)) for i in range(关卡数)]
        
        # 为每个关卡选择最接近目标强度的阵容
        关卡阵容 = []
        for 目标强度 in 目标强度列表:
            最接近的阵容 = min(所有阵容, key=lambda x: abs(cls.计算阵容强度(x) - 目标强度))
            关卡阵容.append(最接近的阵容)
        
        # 平滑强度过渡（改进边界处理）
        关卡强度 = [cls.计算阵容强度(squad) for squad in 关卡阵容]
        平滑强度 = []
        
        # 手动实现滑动平均，确保边界处理正确
        for i in range(关卡数):
            if i == 0:  # 第一个关卡
                平滑强度.append((关卡强度[i] * 0.67) + (关卡强度[i+1] * 0.33))
            elif i == 关卡数 - 1:  # 最后一个关卡
                平滑强度.append((关卡强度[i-1] * 0.33) + (关卡强度[i] * 0.67))
            else:  # 中间关卡
                平滑强度.append((关卡强度[i-1] * 0.33) + (关卡强度[i] * 0.34) + (关卡强度[i+1] * 0.33))
        
        # 重新分配最接近平滑强度的阵容
        最终关卡阵容 = []
        for i in range(关卡数):
            目标强度 = 平滑强度[i]
            最接近的阵容 = min(所有阵容, key=lambda x: abs(cls.计算阵容强度(x) - 目标强度))
            最终关卡阵容.append(最接近的阵容)
        
        return 最终关卡阵容

    @classmethod
    def 获取关卡强度列表(cls, 所有阵容,关卡数=100) -> list[float]:
        """获取关卡强度列表"""
        关卡阵容 = cls.分配关卡阵容(所有阵容,关卡数)
        关卡强度列表 = [cls.计算阵容强度(squad) for squad in 关卡阵容]
        return 关卡强度列表

    @classmethod
    def 计算关卡阶段角色强度要求(cls, 关卡强度列表: list[float]) -> dict:
        """
        根据关卡强度列表计算各关卡阶段对不同品质角色的强度要求
        
        Args:
            关卡强度列表: 每个关卡的强度列表
            
        Returns:
            dict: 各关卡阶段不同品质角色的强度要求
        """
        # 确保关卡强度列表长度正确
        if len(关卡强度列表) != 100:
            raise ValueError(f"关卡强度列表长度应为100，当前为{len(关卡强度列表)}")
        
        # 计算各关卡阶段的平均强度
        阶段1平均强度 = sum(关卡强度列表[:30]) / 30
        阶段2平均强度 = sum(关卡强度列表[30:60]) / 30
        阶段3平均强度 = sum(关卡强度列表[60:]) / 40
        
        # 根据关卡阶段特性计算各品质角色的强度要求
        阶段1要求 = {
            "绿色": 阶段1平均强度 / 3,  # 假设3个相同角色组成阵容
            "蓝色": 阶段1平均强度 / 3 / 1.2,  # 绿色比蓝色高20%，所以蓝色需求是绿色的1/1.2
            "紫色": 阶段1平均强度 / 3 / 1.2 / 1.2  # 绿色比蓝色高20%，蓝色比紫色高20%
        }
        
        阶段2要求 = {
            "绿色": 阶段2平均强度 / 3 / 1.2,  # 蓝色比绿色高20%
            "蓝色": 阶段2平均强度 / 3,
            "紫色": 阶段2平均强度 / 3 / 1.2  # 蓝色比紫色高20%
        }
        
        阶段3要求 = {
            "绿色": 阶段3平均强度 / 3 / 1.2,  # 紫色比绿色高20%
            "蓝色": 阶段3平均强度 / 3 / 1.2,  # 紫色比蓝色高20%
            "紫色": 阶段3平均强度 / 3
        }
        
        return {
            "1-30关": 阶段1要求,
            "31-60关": 阶段2要求,
            "61-100关": 阶段3要求
        }


if __name__ == "__main__":
     # 初始化阵容强度计算类的角色强度表和排序后的角色列表
    阵容强度计算.角色强度表 = 阵容强度计算.初始化角色强度表()
    阵容强度计算.排序后的角色 = 阵容强度计算.初始化排序后的角色()
    所有阵容 = 阵容强度计算.生成所有阵容(阵容强度计算.角色品质)
    
    # 测试阵容强度相关方法
    print("=" * 50)
    print("测试阵容强度相关方法")
    print("=" * 50)
    
    # 测试计算阵容强度范围
    print("\n1. 计算阵容强度范围:")
    阵容强度范围 = 阵容强度计算.计算阵容强度范围()
    print(f"阵容强度范围: {阵容强度范围}")
    
    # 测试计算所有组合数
    print("\n2. 计算所有组合数:")
    组合数 = 阵容强度计算.计算所有组合数()
    print(f"所有组合数: {组合数}")
    
    # 测试计算强度步长
    print("\n3. 计算强度步长:")
    强度步长 = 阵容强度计算.计算强度步长()
    print(f"强度步长: {强度步长}")
    
    # 测试计算关卡阶段角色强度要求
    print("\n4. 计算关卡阶段角色强度要求:")
    关卡强度列表 = 阵容强度计算.获取关卡强度列表(所有阵容)
    关卡阶段强度要求 = 阵容强度计算.计算关卡阶段角色强度要求(关卡强度列表)
    
    print("各关卡阶段角色强度要求:")
    for 阶段, 要求 in 关卡阶段强度要求.items():
        print(f"  {阶段}: {要求}")




        
    



