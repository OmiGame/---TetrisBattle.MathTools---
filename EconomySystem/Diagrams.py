"""根据总产出和总需求，生成图表"""
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Tuple
import os
from EconomySystem.TotalSupply import 系统产出金币和碎片计算,系统产出钻石和钻石宝箱等级计算
from EconomySystem.TotalDemand import 角色碎片计算
from LubanData import tables

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ----
# 1. 数据获取（纯数据）
# ----
每日产出数据 = 系统产出钻石和钻石宝箱等级计算.获取实际的玩家每日系统产出()
每日需求数据 = 角色碎片计算.生成完整每日角色需求详细数据()

普通宝箱获得次数 = tables.Tb经济系统配置表.get("普通宝箱").获得次数
精致宝箱获得次数 = tables.Tb经济系统配置表.get("精致宝箱").获得次数
每日商店获得次数 = tables.Tb经济系统配置表.get("每日商店").获得次数

# ----
# 2. 图表生成器类
# ----
class 资源累积图表生成器:
    """资源累积对比图表生成器
    
    用于生成产出与需求的累积对比图表，包括：
    - 各种资源的累积产出曲线
    - 各种资源的累积需求曲线  
    - 产出与需求的差值分析
    """
    
    def __init__(self, 产出数据: dict, 需求数据: dict):
        """初始化图表生成器
        
        Args:
            产出数据: 每日产出数据字典
            需求数据: 每日需求数据字典
        """
        self.产出数据 = 产出数据
        self.需求数据 = 需求数据
        self.资源类型列表 = ["绿色碎片", "蓝色碎片", "紫色碎片", "金币"]
        self.颜色映射 = {
            "绿色碎片": "#2ecc71",
            "蓝色碎片": "#3498db", 
            "紫色碎片": "#9b59b6",
            "金币": "#f1c40f"
        }
        
    def 处理产出数据为累积格式(self):
        """将产出数据转换为累积格式
        
        Returns:
            dict: 各资源类型的累积产出数据，格式为 {资源类型: [累积值列表]}
        """
        累积产出数据 = {资源: [] for 资源 in self.资源类型列表}
        累积值 = {资源: 0 for 资源 in self.资源类型列表}
        
        # 获取所有日期并排序
        所有日期 = sorted(self.产出数据.keys())
        
        for 日期 in 所有日期:
            日产出 = self.产出数据[日期]
            
            # 计算当日各资源总产出
            当日产出 = {资源: 0 for 资源 in self.资源类型列表}
            
            for 系统名称, 系统数据 in 日产出.items():
                # 根据系统类型确定获得次数
                获得次数 = 1  # 默认为1次
                if 系统名称 == "每日商店":
                    获得次数 = 每日商店获得次数
                elif 系统名称 == "普通宝箱":
                    获得次数 = 普通宝箱获得次数
                elif 系统名称 == "精致宝箱":
                    获得次数 = 精致宝箱获得次数
                
                for 资源类型 in self.资源类型列表:
                    if 资源类型 in 系统数据:
                        当日产出[资源类型] += 系统数据[资源类型] * 获得次数
            
            # 累积计算
            for 资源类型 in self.资源类型列表:
                累积值[资源类型] += 当日产出[资源类型]
                累积产出数据[资源类型].append(累积值[资源类型])
                
        return 累积产出数据
    
    def 处理需求数据为累积格式(self) -> Dict[str, List[float]]:
        """将需求数据转换为累积格式
        
        Returns:
            dict: 各资源类型的累积需求数据，格式为 {资源类型: [累积值列表]}
        """
        累积需求数据 = {资源: [] for 资源 in self.资源类型列表}
        累积值 = {资源: 0 for 资源 in self.资源类型列表}
        
        # 处理分阶段的需求数据
        所有日期数据 = {}
        
        # 合并所有阶段的数据
        for 阶段名称, 阶段数据 in self.需求数据.items():
            for 日期, 日数据 in 阶段数据.items():
                所有日期数据[日期] = 日数据
        
        # 获取所有日期并排序
        所有日期 = sorted(所有日期数据.keys())
        
        for 日期 in 所有日期:
            日需求 = 所有日期数据[日期]
            
            # 提取当日各资源需求
            当日需求 = {
                "绿色碎片": 日需求.get("各品质碎片数", {}).get("绿色", 0),
                "蓝色碎片": 日需求.get("各品质碎片数", {}).get("蓝色", 0),  
                "紫色碎片": 日需求.get("各品质碎片数", {}).get("紫色", 0),
                "金币": 日需求.get("每日金币总产出", 0)
            }
            
            # 累积计算
            for 资源类型 in self.资源类型列表:
                累积值[资源类型] += 当日需求[资源类型]
                累积需求数据[资源类型].append(累积值[资源类型])
                
        return 累积需求数据
    
    def 处理产出数据为每日格式(self) -> Dict[str, List[float]]:
        """将产出数据转换为每日格式
        
        Returns:
            dict: 各资源类型的每日产出数据，格式为 {资源类型: [每日值列表]}
        """
        每日产出数据 = {资源: [] for 资源 in self.资源类型列表}
        
        # 获取实际的日期列表
        日期列表 = self.生成日期列表()
        
        for 日 in 日期列表:
            当日产出 = {资源: 0 for 资源 in self.资源类型列表}
            
            if 日 in self.产出数据:
                日产出 = self.产出数据[日]
                
                for 系统名称, 系统数据 in 日产出.items():
                    # 根据系统类型确定获得次数
                    获得次数 = 1  # 默认为1次
                    if 系统名称 == "每日商店":
                        获得次数 = 每日商店获得次数
                    elif 系统名称 == "普通宝箱":
                        获得次数 = 普通宝箱获得次数
                    elif 系统名称 == "精致宝箱":
                        获得次数 = 精致宝箱获得次数
                    
                    for 资源类型 in self.资源类型列表:
                        if 资源类型 in 系统数据:
                            当日产出[资源类型] += 系统数据[资源类型] * 获得次数
            
            # 记录每日产出
            for 资源类型 in self.资源类型列表:
                每日产出数据[资源类型].append(当日产出[资源类型])
                
        return 每日产出数据
    
    def 处理需求数据为每日格式(self) -> Dict[str, List[float]]:
        """将需求数据转换为每日格式
        
        Returns:
            dict: 各资源类型的每日需求数据，格式为 {资源类型: [每日值列表]}
        """
        每日需求数据 = {资源: [] for 资源 in self.资源类型列表}
        
        # 处理分阶段的需求数据
        所有日期数据 = {}
        
        # 合并所有阶段的数据
        for 阶段名称, 阶段数据 in self.需求数据.items():
            for 日期, 日数据 in 阶段数据.items():
                所有日期数据[日期] = 日数据
        
        # 获取所有日期并排序
        所有日期 = sorted(所有日期数据.keys())
        
        for 日期 in 所有日期:
            日需求 = 所有日期数据[日期]
            
            # 提取当日各资源需求
            当日需求 = {
                "绿色碎片": 日需求.get("各品质碎片数", {}).get("绿色", 0),
                "蓝色碎片": 日需求.get("各品质碎片数", {}).get("蓝色", 0),  
                "紫色碎片": 日需求.get("各品质碎片数", {}).get("紫色", 0),
                "金币": 日需求.get("每日金币总产出", 0)
            }
            
            # 记录每日需求
            for 资源类型 in self.资源类型列表:
                每日需求数据[资源类型].append(当日需求[资源类型])
                
        return 每日需求数据
    
    def 生成日期列表(self) -> List[int]:
        """生成日期列表
        
        Returns:
            list: 日期列表
        """
        # 获取产出数据的所有日期
        产出日期 = set(self.产出数据.keys())
        
        # 获取需求数据的所有日期
        需求日期 = set()
        for 阶段数据 in self.需求数据.values():
            需求日期.update(阶段数据.keys())
        
        # 合并并排序所有日期
        所有日期 = sorted(产出日期.union(需求日期))
        return 所有日期
    
    def 生成单资源对比图(self, 资源类型: str, 保存路径: str = None) -> str:
        """生成单个资源的产出需求对比图
        
        Args:
            资源类型: 要生成图表的资源类型
            保存路径: 图片保存路径，如果为None则自动生成
            
        Returns:
            str: 保存的图片文件路径
        """
        if 资源类型 not in self.资源类型列表:
            raise ValueError(f"不支持的资源类型: {资源类型}")
        
        # 处理数据
        累积产出数据 = self.处理产出数据为累积格式()
        累积需求数据 = self.处理需求数据为累积格式()
        日期列表 = self.生成日期列表()
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 绘制产出曲线
        ax.plot(日期列表, 累积产出数据[资源类型], 
                color=self.颜色映射[资源类型], linewidth=2, 
                label=f'{资源类型}累积产出', marker='o', markersize=4)
        
        # 绘制需求曲线
        ax.plot(日期列表, 累积需求数据[资源类型], 
                color=self.颜色映射[资源类型], linewidth=2, linestyle='--',
                label=f'{资源类型}累积需求', marker='s', markersize=4)
        
        # 填充产出与需求的差值区域
        产出数据 = 累积产出数据[资源类型]
        需求数据 = 累积需求数据[资源类型]
        差值 = [产出 - 需求 for 产出, 需求 in zip(产出数据, 需求数据)]
        
        # 正差值用绿色填充，负差值用红色填充
        ax.fill_between(日期列表, 0, 差值, 
                       where=[d >= 0 for d in 差值], 
                       color='lightgreen', alpha=0.3, label='产出盈余')
        ax.fill_between(日期列表, 0, 差值,
                       where=[d < 0 for d in 差值], 
                       color='lightcoral', alpha=0.3, label='产出不足')
        
        # 设置图表样式
        ax.set_xlabel('游戏天数', fontsize=12)
        ax.set_ylabel(f'{资源类型}数量', fontsize=12)
        ax.set_title(f'{资源类型}累积产出与需求对比图', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 格式化数值显示
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        if 保存路径 is None:
            保存路径 = f'{资源类型}_累积对比图.png'
        
        plt.savefig(保存路径, dpi=300, bbox_inches='tight')
        plt.close()
        
        return 保存路径
    
    def 生成综合对比图(self, 保存路径: str = None) -> str:
        """生成所有资源的综合对比图
        
        Args:
            保存路径: 图片保存路径，如果为None则自动生成
            
        Returns:
            str: 保存的图片文件路径
        """
        # 处理数据
        累积产出数据 = self.处理产出数据为累积格式()
        累积需求数据 = self.处理需求数据为累积格式()
        日期列表 = self.生成日期列表()
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        for i, 资源类型 in enumerate(self.资源类型列表):
            ax = axes[i]
            
            # 绘制产出和需求曲线
            ax.plot(日期列表, 累积产出数据[资源类型], 
                    color=self.颜色映射[资源类型], linewidth=2,
                    label=f'累积产出', marker='o', markersize=3)
            ax.plot(日期列表, 累积需求数据[资源类型], 
                    color=self.颜色映射[资源类型], linewidth=2, linestyle='--',
                    label=f'累积需求', marker='s', markersize=3)
            
            # 计算并显示差值
            产出数据 = 累积产出数据[资源类型]
            需求数据 = 累积需求数据[资源类型]
            差值 = [产出 - 需求 for 产出, 需求 in zip(产出数据, 需求数据)]
            
            # 填充差值区域
            ax.fill_between(日期列表, 0, 差值,
                           where=[d >= 0 for d in 差值],
                           color='lightgreen', alpha=0.3)
            ax.fill_between(日期列表, 0, 差值,
                           where=[d < 0 for d in 差值],
                           color='lightcoral', alpha=0.3)
            
            # 设置子图样式
            ax.set_title(f'{资源类型}累积对比', fontsize=12, fontweight='bold')
            ax.set_xlabel('游戏天数', fontsize=10)
            ax.set_ylabel(f'{资源类型}数量', fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        # 设置总标题
        fig.suptitle('资源累积产出与需求综合对比图', fontsize=16, fontweight='bold')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        if 保存路径 is None:
            保存路径 = '资源累积综合对比图.png'
        
        plt.savefig(保存路径, dpi=300, bbox_inches='tight')
        plt.close()
        
        return 保存路径
    
    def 生成差值分析图(self, 保存路径: str = None) -> str:
        """生成产出与需求差值分析图
        
        Args:
            保存路径: 图片保存路径，如果为None则自动生成
            
        Returns:
            str: 保存的图片文件路径
        """
        # 处理数据
        累积产出数据 = self.处理产出数据为累积格式()
        累积需求数据 = self.处理需求数据为累积格式()
        日期列表 = self.生成日期列表()
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for 资源类型 in self.资源类型列表:
            产出数据 = 累积产出数据[资源类型]
            需求数据 = 累积需求数据[资源类型]
            差值 = [产出 - 需求 for 产出, 需求 in zip(产出数据, 需求数据)]
            
            ax.plot(日期列表, 差值, 
                    color=self.颜色映射[资源类型], linewidth=2,
                    label=f'{资源类型}差值', marker='o', markersize=4)
        
        # 添加零线
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
        
        # 设置图表样式
        ax.set_xlabel('游戏天数', fontsize=12)
        ax.set_ylabel('产出-需求差值', fontsize=12)
        ax.set_title('各资源产出与需求差值分析图', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 格式化数值显示
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        if 保存路径 is None:
            保存路径 = '资源差值分析图.png'
        
        plt.savefig(保存路径, dpi=300, bbox_inches='tight')
        plt.close()
        
        return 保存路径

    def 生成单资源每日对比图(self, 资源类型: str, 保存路径: str = None) -> str:
        """生成单个资源的每日产出需求对比图
        
        Args:
            资源类型: 要生成图表的资源类型
            保存路径: 图片保存路径，如果为None则自动生成
            
        Returns:
            str: 保存的图片文件路径
        """
        if 资源类型 not in self.资源类型列表:
            raise ValueError(f"不支持的资源类型: {资源类型}")
        
        # 处理数据
        每日产出数据 = self.处理产出数据为每日格式()
        每日需求数据 = self.处理需求数据为每日格式()
        日期列表 = self.生成日期列表()
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # 上图：每日产出和需求对比
        产出数据 = 每日产出数据[资源类型]
        需求数据 = 每日需求数据[资源类型]
        
        # 绘制柱状图
        宽度 = 0.35
        x_pos = np.arange(len(日期列表))
        
        bars1 = ax1.bar(x_pos - 宽度/2, 产出数据, 宽度, 
                       color=self.颜色映射[资源类型], alpha=0.8, 
                       label=f'{资源类型}每日产出')
        bars2 = ax1.bar(x_pos + 宽度/2, 需求数据, 宽度,
                       color=self.颜色映射[资源类型], alpha=0.5, 
                       label=f'{资源类型}每日需求', hatch='//')
        
        # 设置上图样式
        ax1.set_xlabel('游戏天数', fontsize=12)
        ax1.set_ylabel(f'{资源类型}数量', fontsize=12)
        ax1.set_title(f'{资源类型}每日产出与需求对比', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_pos[::5])  # 每5天显示一个刻度
        ax1.set_xticklabels([str(日期列表[i]) for i in range(0, len(日期列表), 5)])
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        # 下图：每日差值
        差值数据 = [产出 - 需求 for 产出, 需求 in zip(产出数据, 需求数据)]
        
        # 用不同颜色表示正负差值
        颜色列表 = ['lightgreen' if d >= 0 else 'lightcoral' for d in 差值数据]
        
        bars3 = ax2.bar(x_pos, 差值数据, color=颜色列表, alpha=0.7,
                       label=f'{资源类型}每日差值')
        
        # 添加零线
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
        
        # 设置下图样式
        ax2.set_xlabel('游戏天数', fontsize=12)
        ax2.set_ylabel(f'{资源类型}差值 (产出-需求)', fontsize=12)
        ax2.set_title(f'{资源类型}每日产出需求差值', fontsize=12, fontweight='bold')
        ax2.set_xticks(x_pos[::5])
        ax2.set_xticklabels([str(日期列表[i]) for i in range(0, len(日期列表), 5)])
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        if 保存路径 is None:
            保存路径 = f'{资源类型}_每日对比图.png'
        
        plt.savefig(保存路径, dpi=300, bbox_inches='tight')
        plt.close()
        
        return 保存路径
    
    def 生成每日综合对比图(self, 保存路径: str = None) -> str:
        """生成所有资源的每日对比图
        
        Args:
            保存路径: 图片保存路径，如果为None则自动生成
            
        Returns:
            str: 保存的图片文件路径
        """
        # 处理数据
        每日产出数据 = self.处理产出数据为每日格式()
        每日需求数据 = self.处理需求数据为每日格式()
        日期列表 = self.生成日期列表()
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, 资源类型 in enumerate(self.资源类型列表):
            ax = axes[i]
            
            产出数据 = 每日产出数据[资源类型]
            需求数据 = 每日需求数据[资源类型]
            
            # 绘制每日产出和需求
            宽度 = 0.35
            x_pos = np.arange(len(日期列表))
            
            ax.bar(x_pos - 宽度/2, 产出数据, 宽度,
                   color=self.颜色映射[资源类型], alpha=0.8,
                   label='每日产出')
            ax.bar(x_pos + 宽度/2, 需求数据, 宽度,
                   color=self.颜色映射[资源类型], alpha=0.5,
                   label='每日需求', hatch='//')
            
            # 设置子图样式
            ax.set_title(f'{资源类型}每日对比', fontsize=12, fontweight='bold')
            ax.set_xlabel('游戏天数', fontsize=10)
            ax.set_ylabel(f'{资源类型}数量', fontsize=10)
            ax.set_xticks(x_pos[::10])  # 每10天显示一个刻度
            ax.set_xticklabels([str(日期列表[i]) for i in range(0, len(日期列表), 10)])
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        # 设置总标题
        fig.suptitle('各资源每日产出与需求综合对比图', fontsize=16, fontweight='bold')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        if 保存路径 is None:
            保存路径 = '资源每日综合对比图.png'
        
        plt.savefig(保存路径, dpi=300, bbox_inches='tight')
        plt.close()
        
        return 保存路径
    
    def 生成每日差值对比图(self, 保存路径: str = None) -> str:
        """生成各资源每日差值对比图
        
        Args:
            保存路径: 图片保存路径，如果为None则自动生成
            
        Returns:
            str: 保存的图片文件路径
        """
        # 处理数据
        每日产出数据 = self.处理产出数据为每日格式()
        每日需求数据 = self.处理需求数据为每日格式()
        日期列表 = self.生成日期列表()
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(16, 8))
        
        宽度 = 0.2
        x_pos = np.arange(len(日期列表))
        
        for i, 资源类型 in enumerate(self.资源类型列表):
            产出数据 = 每日产出数据[资源类型]
            需求数据 = 每日需求数据[资源类型]
            差值数据 = [产出 - 需求 for 产出, 需求 in zip(产出数据, 需求数据)]
            
            ax.bar(x_pos + i * 宽度, 差值数据, 宽度,
                   color=self.颜色映射[资源类型], alpha=0.7,
                   label=f'{资源类型}差值')
        
        # 添加零线
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
        
        # 设置图表样式
        ax.set_xlabel('游戏天数', fontsize=12)
        ax.set_ylabel('每日差值 (产出-需求)', fontsize=12)
        ax.set_title('各资源每日产出需求差值对比图', fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos[::5] + 宽度 * 1.5)  # 调整刻度位置
        ax.set_xticklabels([str(日期列表[i]) for i in range(0, len(日期列表), 5)])
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        if 保存路径 is None:
            保存路径 = '资源每日差值对比图.png'
        
        plt.savefig(保存路径, dpi=300, bbox_inches='tight')
        plt.close()
        
        return 保存路径

# ----
# 3. 便捷函数
# ----
def 生成所有资源图表(输出目录: str = "图表输出") -> List[str]:
    """生成所有资源的图表
    
    Args:
        输出目录: 图表保存目录
        
    Returns:
        list: 生成的图表文件路径列表
    """
    # 确保输出目录存在
    os.makedirs(输出目录, exist_ok=True)
    
    # 创建图表生成器
    图表生成器 = 资源累积图表生成器(每日产出数据, 每日需求数据)
    
    生成的文件列表 = []
    
    # 生成单个资源图表
    for 资源类型 in ["绿色碎片", "蓝色碎片", "紫色碎片", "金币"]:
        文件路径 = os.path.join(输出目录, f'{资源类型}_累积对比图.png')
        图表生成器.生成单资源对比图(资源类型, 文件路径)
        生成的文件列表.append(文件路径)
    
    # 生成综合对比图
    综合图路径 = os.path.join(输出目录, '资源累积综合对比图.png')
    图表生成器.生成综合对比图(综合图路径)
    生成的文件列表.append(综合图路径)
    
    # 生成差值分析图
    差值图路径 = os.path.join(输出目录, '资源差值分析图.png')
    图表生成器.生成差值分析图(差值图路径)
    生成的文件列表.append(差值图路径)
    
    # 生成单资源每日对比图
    for 资源类型 in ["绿色碎片", "蓝色碎片", "紫色碎片", "金币"]:
        文件路径 = os.path.join(输出目录, f'{资源类型}_每日对比图.png')
        图表生成器.生成单资源每日对比图(资源类型, 文件路径)
        生成的文件列表.append(文件路径)
    
    # 生成每日综合对比图
    每日综合对比图路径 = os.path.join(输出目录, '资源每日综合对比图.png')
    图表生成器.生成每日综合对比图(每日综合对比图路径)
    生成的文件列表.append(每日综合对比图路径)
    
    # 生成每日差值对比图
    每日差值对比图路径 = os.path.join(输出目录, '资源每日差值对比图.png')
    图表生成器.生成每日差值对比图(每日差值对比图路径)
    生成的文件列表.append(每日差值对比图路径)
    
    return 生成的文件列表

def 打印数据摘要():
    """打印产出和需求数据的摘要信息"""
    print("=" * 50)
    print("经济系统数据摘要")
    print("=" * 50)
    
    print(f"产出数据覆盖天数: {len(每日产出数据)}")
    print(f"需求数据阶段数: {len(每日需求数据)}")
    
    # 统计需求数据总天数
    总需求天数 = sum(len(阶段数据) for 阶段数据 in 每日需求数据.values())
    print(f"需求数据覆盖天数: {总需求天数}")
    
    print("\n各阶段需求数据详情:")
    for 阶段名称, 阶段数据 in 每日需求数据.items():
        print(f"  {阶段名称}: {len(阶段数据)}天")
    
    print("\n" + "=" * 50)

def 生成每日对比图表(输出目录: str = "图表输出") -> List[str]:
    """生成所有资源的每日对比图表
    
    Args:
        输出目录: 图表保存目录
        
    Returns:
        list: 生成的每日对比图表文件路径列表
    """
    # 确保输出目录存在
    os.makedirs(输出目录, exist_ok=True)
    
    # 创建图表生成器
    图表生成器 = 资源累积图表生成器(每日产出数据, 每日需求数据)
    
    生成的文件列表 = []
    
    # 生成单资源每日对比图
    for 资源类型 in ["绿色碎片", "蓝色碎片", "紫色碎片", "金币"]:
        文件路径 = os.path.join(输出目录, f'{资源类型}_每日对比图.png')
        图表生成器.生成单资源每日对比图(资源类型, 文件路径)
        生成的文件列表.append(文件路径)
    
    # 生成每日综合对比图
    每日综合对比图路径 = os.path.join(输出目录, '资源每日综合对比图.png')
    图表生成器.生成每日综合对比图(每日综合对比图路径)
    生成的文件列表.append(每日综合对比图路径)
    
    # 生成每日差值对比图
    每日差值对比图路径 = os.path.join(输出目录, '资源每日差值对比图.png')
    图表生成器.生成每日差值对比图(每日差值对比图路径)
    生成的文件列表.append(每日差值对比图路径)
    
    return 生成的文件列表

# ----
# 4. 玩家看广告情况图表生成器
# ----
class 玩家看广告情况图表生成器:
    """玩家看广告情况图表生成器
    
    用于根据传入的广告参数生成玩家实际产出图表
    """
    
    def __init__(self, 看钻石广告百分比: float = 1.0, 看金币广告百分比: float = 1.0, 看精致宝箱广告百分比: float = 1.0, 钻石金币商店购买比例: float = 0.0):
        """初始化图表生成器
        
        Args:
            看钻石广告百分比: 看钻石广告的百分比 (0.0-1.0)
            看金币广告百分比: 看金币广告的百分比 (0.0-1.0)  
            看精致宝箱广告百分比: 看精致宝箱广告的百分比 (0.0-1.0)
            钻石金币商店购买比例: 用钻石购买金币的比例 (0.0-1.0)
        """
        self.看钻石广告百分比 = 看钻石广告百分比
        self.看金币广告百分比 = 看金币广告百分比
        self.看精致宝箱广告百分比 = 看精致宝箱广告百分比
        self.钻石金币商店购买比例 = 钻石金币商店购买比例
        
        # 导入必要的类
        from EconomySystem.TotalSupply import 系统产出钻石和钻石宝箱等级计算
        
        # 计算玩家实际产出数据
        self.玩家实际产出数据 = 系统产出钻石和钻石宝箱等级计算.获取实际的玩家每日系统产出()
        
        # 获取玩家实际的宝箱获得次数
        self.玩家实际宝箱获得次数 = self._计算玩家实际宝箱获得次数()
        
        # 获取需求数据
        self.需求数据 = 每日需求数据
        
        # 资源类型和颜色映射
        self.资源类型列表 = ["绿色碎片", "蓝色碎片", "紫色碎片", "金币"]
        self.颜色映射 = {
            "绿色碎片": "#2ecc71",
            "蓝色碎片": "#3498db", 
            "紫色碎片": "#9b59b6",
            "金币": "#f1c40f"
        }
    
    def _计算玩家实际宝箱获得次数(self) -> Dict[str, int]:
        """计算玩家实际的宝箱获得次数"""
        from EconomySystem.TotalSupply import 系统产出钻石和钻石宝箱等级计算
        
        # 调用TotalSupply模块中的新函数
        宝箱和金币数据 = 系统产出钻石和钻石宝箱等级计算._玩家实际获得宝箱和金币数(
            看钻石广告百分比=self.看钻石广告百分比,
            看金币广告百分比=self.看金币广告百分比,
            看精致宝箱广告百分比=self.看精致宝箱广告百分比,
            钻石金币商店购买比例=self.钻石金币商店购买比例
        )
        
        return {
            "普通宝箱获得次数": int(宝箱和金币数据["普通宝箱获得次数"]),
            "精致宝箱获得次数": int(宝箱和金币数据["精致宝箱获得次数"]),
            "每日少领取金币": int(宝箱和金币数据["每日少领取金币"]),
        }
    
    def 处理产出数据为累积格式(self):
        """将产出数据处理为累积格式"""
        累积数据 = {资源: [] for 资源 in self.资源类型列表}
        
        # 获取实际的日期列表
        日期列表 = self.生成日期列表()
        
        for 日 in 日期列表:
            当日产出 = {资源: 0 for 资源 in self.资源类型列表}
            
            if 日 in self.玩家实际产出数据:
                日产出 = self.玩家实际产出数据[日]
                
                for 系统名称, 系统数据 in 日产出.items():
                    # 根据系统类型确定获得次数
                    获得次数 = 1  # 默认为1次
                    if 系统名称 == "普通宝箱":
                        获得次数 = self.玩家实际宝箱获得次数["普通宝箱获得次数"]
                    elif 系统名称 == "精致宝箱":
                        获得次数 = self.玩家实际宝箱获得次数["精致宝箱获得次数"]
                    
                    for 资源类型 in self.资源类型列表:
                        if 资源类型 in 系统数据:
                            当日产出[资源类型] += 系统数据[资源类型] * 获得次数
            
            # 减去少领取的金币
            当日产出["金币"] -= self.玩家实际宝箱获得次数["每日少领取金币"]
            
            # 累积计算
            for 资源 in self.资源类型列表:
                前日累积值 = 累积数据[资源][-1] if 累积数据[资源] else 0
                累积数据[资源].append(前日累积值 + 当日产出[资源])
                
        return 累积数据
    
    def 处理产出数据为每日格式(self) -> Dict[str, List[float]]:
        """将产出数据转换为每日格式
        
        Returns:
            dict: 各资源类型的每日产出数据，格式为 {资源类型: [每日值列表]}
        """
        每日产出数据 = {资源: [] for 资源 in self.资源类型列表}
        
        # 获取实际的日期列表
        日期列表 = self.生成日期列表()
        
        for 日 in 日期列表:
            当日产出 = {资源: 0 for 资源 in self.资源类型列表}
            
            if 日 in self.玩家实际产出数据:
                日产出 = self.玩家实际产出数据[日]
                
                for 系统名称, 系统数据 in 日产出.items():
                    # 根据系统类型确定获得次数
                    获得次数 = 1  # 默认为1次
                    if 系统名称 == "普通宝箱":
                        获得次数 = self.玩家实际宝箱获得次数["普通宝箱获得次数"]
                    elif 系统名称 == "精致宝箱":
                        获得次数 = self.玩家实际宝箱获得次数["精致宝箱获得次数"]
                    
                    for 资源类型 in self.资源类型列表:
                        if 资源类型 in 系统数据:
                            当日产出[资源类型] += 系统数据[资源类型] * 获得次数
            
            # 减去少领取的金币
            当日产出["金币"] -= self.玩家实际宝箱获得次数["每日少领取金币"]
            
            # 记录每日产出
            for 资源类型 in self.资源类型列表:
                每日产出数据[资源类型].append(当日产出[资源类型])
                 
        return 每日产出数据
    
    def 处理需求数据为累积格式(self) -> Dict[str, List[float]]:
        """将需求数据转换为累积格式
        
        Returns:
            dict: 各资源类型的累积需求数据，格式为 {资源类型: [累积值列表]}
        """
        累积需求数据 = {资源: [] for 资源 in self.资源类型列表}
        累积值 = {资源: 0 for 资源 in self.资源类型列表}
        
        # 处理分阶段的需求数据
        所有日期数据 = {}
        
        # 合并所有阶段的数据
        for 阶段名称, 阶段数据 in self.需求数据.items():
            for 日期, 日数据 in 阶段数据.items():
                所有日期数据[日期] = 日数据
        
        # 获取所有日期并排序
        所有日期 = sorted(所有日期数据.keys())
        
        for 日期 in 所有日期:
            日需求 = 所有日期数据[日期]
            
            # 提取当日各资源需求
            当日需求 = {
                "绿色碎片": 日需求.get("各品质碎片数", {}).get("绿色", 0),
                "蓝色碎片": 日需求.get("各品质碎片数", {}).get("蓝色", 0),  
                "紫色碎片": 日需求.get("各品质碎片数", {}).get("紫色", 0),
                "金币": 日需求.get("每日金币总产出", 0)
            }
            
            # 累积计算
            for 资源类型 in self.资源类型列表:
                累积值[资源类型] += 当日需求[资源类型]
                累积需求数据[资源类型].append(累积值[资源类型])
                
        return 累积需求数据
    
    def 处理产出数据为每日格式(self) -> Dict[str, List[float]]:
        """将产出数据转换为每日格式
        
        Returns:
            dict: 各资源类型的每日产出数据，格式为 {资源类型: [每日值列表]}
        """
        每日产出数据 = {资源: [] for 资源 in self.资源类型列表}
        
        # 获取实际的日期列表
        日期列表 = self.生成日期列表()
        
        for 日 in 日期列表:
            当日产出 = {资源: 0 for 资源 in self.资源类型列表}
            
            if 日 in self.玩家实际产出数据:
                日产出 = self.玩家实际产出数据[日]
                
                for 系统名称, 系统数据 in 日产出.items():
                    # 根据系统类型确定获得次数
                    获得次数 = 1  # 默认为1次
                    if 系统名称 == "普通宝箱":
                        获得次数 = self.玩家实际宝箱获得次数["普通宝箱获得次数"]
                    elif 系统名称 == "精致宝箱":
                        获得次数 = self.玩家实际宝箱获得次数["精致宝箱获得次数"]
                    
                    for 资源类型 in self.资源类型列表:
                        if 资源类型 in 系统数据:
                            产出量 = 系统数据[资源类型] * 获得次数
                            
                            # 对金币系统进行特殊处理：减去每日少领取金币
                            if 资源类型 == "金币" and 系统名称 == "金币商店":
                                产出量 -= self.玩家实际宝箱获得次数["每日少领取金币"]
                            
                            当日产出[资源类型] += 产出量
            
            # 记录每日产出
            for 资源类型 in self.资源类型列表:
                每日产出数据[资源类型].append(当日产出[资源类型])
                 
        return 每日产出数据
    
    def 处理需求数据为每日格式(self) -> Dict[str, List[float]]:
        """将需求数据转换为每日格式
        
        Returns:
            dict: 各资源类型的每日需求数据，格式为 {资源类型: [每日值列表]}
        """
        每日需求数据 = {资源: [] for 资源 in self.资源类型列表}
        
        # 处理分阶段的需求数据
        所有日期数据 = {}
        
        # 合并所有阶段的数据
        for 阶段名称, 阶段数据 in self.需求数据.items():
            for 日期, 日数据 in 阶段数据.items():
                所有日期数据[日期] = 日数据
        
        # 获取所有日期并排序
        所有日期 = sorted(所有日期数据.keys())
        
        for 日期 in 所有日期:
            日需求 = 所有日期数据[日期]
            
            # 提取当日各资源需求
            当日需求 = {
                "绿色碎片": 日需求.get("各品质碎片数", {}).get("绿色", 0),
                "蓝色碎片": 日需求.get("各品质碎片数", {}).get("蓝色", 0),  
                "紫色碎片": 日需求.get("各品质碎片数", {}).get("紫色", 0),
                "金币": 日需求.get("每日金币总产出", 0)
            }
            
            # 记录每日需求
            for 资源类型 in self.资源类型列表:
                每日需求数据[资源类型].append(当日需求[资源类型])
                
        return 每日需求数据
    
    def 生成日期列表(self) -> List[int]:
        """生成日期列表
        
        Returns:
            list: 日期列表
        """
        # 获取产出数据的所有日期
        产出日期 = set(self.玩家实际产出数据.keys())
        
        # 获取需求数据的所有日期
        需求日期 = set()
        for 阶段数据 in self.需求数据.values():
            需求日期.update(阶段数据.keys())
        
        # 合并并排序所有日期
        所有日期 = sorted(产出日期.union(需求日期))
        return 所有日期
    
    def 生成参数文件夹名称(self) -> str:
        """生成参数文件夹名称
        
        Returns:
            str: 文件夹名称，格式为 "钻石广告{value}_金币广告{value}_精致宝箱广告{value}_钻石金币购买{value}"
        """
        钻石百分比 = int(self.看钻石广告百分比 * 100)
        金币百分比 = int(self.看金币广告百分比 * 100)
        精致宝箱百分比 = int(self.看精致宝箱广告百分比 * 100)
        钻石金币购买百分比 = int(self.钻石金币商店购买比例 * 100)
        
        return f"钻石广告{钻石百分比}_金币广告{金币百分比}_精致宝箱广告{精致宝箱百分比}_钻石金币购买{钻石金币购买百分比}"

def 生成玩家看广告情况图表(看钻石广告百分比: float = 1.0, 看金币广告百分比: float = 1.0, 看精致宝箱广告百分比: float = 1.0, 钻石金币商店购买比例: float = 0.0, 输出基础目录: str = "图表输出") -> List[str]:
    """生成玩家看广告情况的所有图表
    
    Args:
        看钻石广告百分比: 看钻石广告的百分比 (0.0-1.0)
        看金币广告百分比: 看金币广告的百分比 (0.0-1.0)
        看精致宝箱广告百分比: 看精致宝箱广告的百分比 (0.0-1.0)
        钻石金币商店购买比例: 用钻石购买金币的比例 (0.0-1.0)
        输出基础目录: 图表保存基础目录
        
    Returns:
        list: 生成的图表文件路径列表
    """
    # 创建玩家看广告情况图表生成器
    广告图表生成器 = 玩家看广告情况图表生成器(看钻石广告百分比, 看金币广告百分比, 看精致宝箱广告百分比, 钻石金币商店购买比例)
    
    # 生成参数文件夹名称
    参数文件夹名称 = 广告图表生成器.生成参数文件夹名称()
    
    # 创建输出目录
    输出目录 = os.path.join(输出基础目录, 参数文件夹名称)
    os.makedirs(输出目录, exist_ok=True)
    
    生成的文件列表 = []
    
    print(f"=== 开始生成玩家看广告情况图表 ===")
    print(f"参数设置：钻石广告{看钻石广告百分比*100:.0f}%，金币广告{看金币广告百分比*100:.0f}%，精致宝箱广告{看精致宝箱广告百分比*100:.0f}%")
    print(f"输出目录：{输出目录}")
    print(f"玩家实际宝箱获得次数：{广告图表生成器.玩家实际宝箱获得次数}")
    
    # 使用资源累积图表生成器的逻辑，但用玩家实际产出数据
    # 创建一个临时的资源累积图表生成器，替换产出数据
    class 临时图表生成器(资源累积图表生成器):
        def __init__(self, 玩家实际产出数据, 需求数据, 玩家实际宝箱获得次数):
            self.产出数据 = 玩家实际产出数据
            self.需求数据 = 需求数据
            self.玩家实际宝箱获得次数 = 玩家实际宝箱获得次数
            self.资源类型列表 = ["绿色碎片", "蓝色碎片", "紫色碎片", "金币"]
            self.颜色映射 = {
                "绿色碎片": "#2ecc71",
                "蓝色碎片": "#3498db", 
                "紫色碎片": "#9b59b6",
                "金币": "#f1c40f"
            }
        
        def 处理产出数据为累积格式(self) -> Dict[str, List[float]]:
            return 广告图表生成器.处理产出数据为累积格式()
        
        def 处理产出数据为每日格式(self) -> Dict[str, List[float]]:
            return 广告图表生成器.处理产出数据为每日格式()
        
        def 处理需求数据为累积格式(self) -> Dict[str, List[float]]:
            return 广告图表生成器.处理需求数据为累积格式()
        
        def 处理需求数据为每日格式(self) -> Dict[str, List[float]]:
            return 广告图表生成器.处理需求数据为每日格式()
        
        def 生成日期列表(self) -> List[int]:
            return 广告图表生成器.生成日期列表()
    
    # 创建临时图表生成器
    图表生成器 = 临时图表生成器(广告图表生成器.玩家实际产出数据, 广告图表生成器.需求数据, 广告图表生成器.玩家实际宝箱获得次数)
    
    # 生成单个资源累积对比图
    for 资源类型 in ["绿色碎片", "蓝色碎片", "紫色碎片", "金币"]:
        文件路径 = os.path.join(输出目录, f'{资源类型}_累积对比图.png')
        图表生成器.生成单资源对比图(资源类型, 文件路径)
        生成的文件列表.append(文件路径)
        print(f"✓ 生成 {资源类型}_累积对比图.png")
    
    # 生成综合累积对比图
    综合图路径 = os.path.join(输出目录, '资源累积综合对比图.png')
    图表生成器.生成综合对比图(综合图路径)
    生成的文件列表.append(综合图路径)
    print("✓ 生成 资源累积综合对比图.png")
    
    # 生成差值分析图
    差值图路径 = os.path.join(输出目录, '资源差值分析图.png')
    图表生成器.生成差值分析图(差值图路径)
    生成的文件列表.append(差值图路径)
    print("✓ 生成 资源差值分析图.png")
    
    # 生成单资源每日对比图
    for 资源类型 in ["绿色碎片", "蓝色碎片", "紫色碎片", "金币"]:
        文件路径 = os.path.join(输出目录, f'{资源类型}_每日对比图.png')
        图表生成器.生成单资源每日对比图(资源类型, 文件路径)
        生成的文件列表.append(文件路径)
        print(f"✓ 生成 {资源类型}_每日对比图.png")
    
    # 生成每日综合对比图
    每日综合对比图路径 = os.path.join(输出目录, '资源每日综合对比图.png')
    图表生成器.生成每日综合对比图(每日综合对比图路径)
    生成的文件列表.append(每日综合对比图路径)
    print("✓ 生成 资源每日综合对比图.png")
    
    # 生成每日差值对比图
    每日差值对比图路径 = os.path.join(输出目录, '资源每日差值对比图.png')
    图表生成器.生成每日差值对比图(每日差值对比图路径)
    生成的文件列表.append(每日差值对比图路径)
    print("✓ 生成 资源每日差值对比图.png")
    
    print(f"\n=== 图表生成完成 ===")
    print(f"共生成 {len(生成的文件列表)} 个图表文件")
    print(f"保存位置：{输出目录}")
    
    return 生成的文件列表

def 生成多组玩家看广告情况图表(参数组合列表: List[Tuple[float, float, float]], 输出基础目录: str = "图表输出") -> Dict[str, List[str]]:
    """生成多组不同参数的玩家看广告情况图表
    
    Args:
        参数组合列表: 参数组合列表，每个元素为 (看钻石广告百分比, 看金币广告百分比, 看精致宝箱广告百分比)
        输出基础目录: 图表保存基础目录
        
    Returns:
        dict: 各参数组合对应的生成文件列表字典
    """
    所有生成结果 = {}
    
    print(f"=== 开始批量生成玩家看广告情况图表 ===")
    print(f"共 {len(参数组合列表)} 组参数")
    
    for i, (看钻石广告百分比, 看金币广告百分比, 看精致宝箱广告百分比) in enumerate(参数组合列表, 1):
        print(f"\n--- 第 {i}/{len(参数组合列表)} 组参数 ---")
        
        try:
            生成的文件 = 生成玩家看广告情况图表(
                看钻石广告百分比=看钻石广告百分比,
                看金币广告百分比=看金币广告百分比,
                看精致宝箱广告百分比=看精致宝箱广告百分比,
                输出基础目录=输出基础目录
            )
            
            参数组合名称 = f"钻石{int(看钻石广告百分比*100)}_金币{int(看金币广告百分比*100)}_精致宝箱{int(看精致宝箱广告百分比*100)}"
            所有生成结果[参数组合名称] = 生成的文件
            
        except Exception as e:
            print(f"❌ 第 {i} 组参数生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== 批量生成完成 ===")
    print(f"成功生成 {len(所有生成结果)} 组图表")
    
    return 所有生成结果

# ----
# 5. 主执行函数
# ----
if __name__ == "__main__":
    # 打印数据摘要
    打印数据摘要()
    
    # 生成所有默认图表
    try:
        生成的文件 = 生成所有资源图表()
        print(f"\n成功生成{len(生成的文件)}个默认图表文件:")
        for 文件 in 生成的文件:
            print(f"  - {文件}")
    except Exception as e:
        print(f"生成默认图表时发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    
    # 示例：生成不同看广告情况的图表
    try:
        print(f"\n=== 示例：生成玩家看广告情况图表 ===")
        
        # 示例1：完全看广告情况 (100%, 100%, 100%)
        生成玩家看广告情况图表(0, 0, 0, 0.25)
        
    except Exception as e:
        print(f"生成玩家看广告情况图表时发生错误: {e}")
        import traceback
        traceback.print_exc()