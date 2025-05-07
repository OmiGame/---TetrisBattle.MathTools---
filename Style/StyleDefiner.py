from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict
from openpyxl.styles import Font, PatternFill, Alignment, NamedStyle

# -------------------------------------
# 1. 枚举定义（纯数据）
# -------------------------------------
class 表格样式类型(Enum):
    """定义表格的样式类型"""
    角色成长表 = auto()
    怪物表 = auto()
    默认样式 = auto()

class 字体风格(Enum):
    """定义字体的风格类型"""
    常规 = "regular"
    加粗 = "bold"
    斜体 = "italic"
    加粗斜体 = "bold_italic"

class 颜色风格(Enum):
    """所有颜色使用枚举管理，避免拼写错误"""
    白色 = "FFFFFF"
    灰黑 = "424242"
    黑色 = "000000"
    灰色 = "A9A9A9"
    深蓝 = "000080"

# -------------------------------------
# 2. 样式配置类（纯数据结构）
# -------------------------------------
@dataclass
class 字体配置:
    """定义字体的配置"""
    颜色: 颜色风格
    风格: 字体风格 = 字体风格.常规
    大小: int = 11


@dataclass
class 背景配置:
    """定义背景的配置"""
    颜色: 颜色风格
    填充类型: str = "solid"

@dataclass
class 样式配置项:
    """完整的样式配置定义"""
    样式名称: str
    字体: 字体配置
    背景: 背景配置 = None
    对齐方式: Alignment = Alignment(horizontal='center', vertical='center')

# -------------------------------------
# 3. 预设样式库（不同表格类型的样式配置）
# -------------------------------------
#定义 字符串 和 样式配置 的映射，因为openpyxl中有关样式的函数只认字符串
样式预设库: Dict[str, 样式配置项] = {
    # 角色成长表样式
    "header_角色成长": 样式配置项(
        "header_角色成长",
        字体=字体配置(颜色风格.白色, 字体风格.加粗),
        背景=背景配置(颜色风格.灰黑)
    ),
    "data_角色成长": 样式配置项(
        "data_角色成长",
        字体=字体配置(颜色风格.黑色)
    ),

    # 怪物表样式
    "header_怪物表": 样式配置项(
        "header_怪物表",
        字体=字体配置(颜色风格.白色, 字体风格.加粗),
        背景=背景配置(颜色风格.灰黑)
    ),
    "data_怪物表": 样式配置项(
        "data_怪物表",
        字体=字体配置(颜色风格.黑色)
    ),

    # 默认样式
    "header_default": 样式配置项(
        "header_default",
        字体=字体配置(颜色风格.白色, 字体风格.加粗),
        背景=背景配置(颜色风格.灰黑)
    ),
    "data_default": 样式配置项(
        "data_default",
        字体=字体配置(颜色风格.黑色)
    )
}

# 表格类型  与  多个具体样式配置的字符串 的映射
表格样式映射: Dict[表格样式类型, Dict[str, str]] = {
    表格样式类型.角色成长表: {
        "header": "header_角色成长",
        "data": "data_角色成长"
    },
    表格样式类型.怪物表: {
        "header": "header_怪物表",
        "data": "data_怪物表"
    },
    表格样式类型.默认样式: {
        "header": "header_default",
        "data": "data_default"
    }
}

# -------------------------------------
# 4. 样式生成器（逻辑部分）
# -------------------------------------
class 样式生成器:
    @staticmethod
    def 创建样式(配置: 样式配置项) -> NamedStyle:
        """将样式配置转换为openpyxl的NamedStyle"""
        style = NamedStyle(name=配置.样式名称)
        style.font = Font(
            color=配置.字体.颜色.value,
            bold='bold' in 配置.字体.风格.value,
            italic='italic' in 配置.字体.风格.value,
            size=配置.字体.大小
        )
        if 配置.背景:
            style.fill = PatternFill(
                fill_type=配置.背景.填充类型,
                fgColor=配置.背景.颜色.value
            )
        if 配置.对齐方式:
            style.alignment = 配置.对齐方式
        return style

    @classmethod
    def 获取样式名称(cls, 表格样式类型: 表格样式类型, 样式类型: str) -> str:
        """获取指定表格类型的样式名称"""
        return 表格样式映射.get(表格样式类型, 表格样式映射[表格样式类型.默认样式])[样式类型]

    @classmethod
    def 获取样式配置(cls, 样式名称: str) -> 样式配置项:
        """根据名称获取样式配置"""
        return 样式预设库[样式名称]

    @classmethod
    def 清除样式缓存(cls, wb, style_name: str):
        target = style_name
        filtered = [
            style for style in wb._named_styles
            if target not in style.name
        ]
        # wb._named_styles是一个特殊的列表类型，必须转换回去
        wb._named_styles[:] = filtered

    # @classmethod
    # def 清除样式缓存(cls, wb, 样式名称: str):
    #     """确保彻底删除旧样式"""
    #     # 1. 从 _named_styles 中移除
    #     for style in list(wb._named_styles):     # 使用 list() 避免修改时迭代问题
    #         if style.name == 样式名称:
    #             wb._named_styles.remove(style)



        # 如果存在公开接口 wb.named_styles，也同步更新
        # if hasattr(wb, "named_styles"):
        #     wb.named_styles = filtered
        # """
        # 清除工作簿 wb 中，所有 NamedStyle.name 中包含 style_name 的样式
        # """
        #
        # target = style_name.lower()
        # # 只保留名字中不包含 target 的 NamedStyle 实例
        # wb._named_styles = [
        #     ns for ns in wb._named_styles
        #     if target not in ns.name.lower()
        # ]
    #     # 对比时忽略大小写，可根据需要去掉 .lower()
    #     target = style_name.lower()
    #     # 过滤出不包含 target 的样式
    #     wb._named_styles = [
    #         ns for ns in wb._named_styles
    #         if target not in ns.name.lower()
    #     ]
    #     # 如果你也用了 wb.named_styles（公开接口），可同步更新
    #     try:
    #         wb.named_styles = wb._named_styles
    #     except AttributeError:
    #         # 旧版本 openpyxl 可能没有公开属性，忽略即可
    #         pass
    #
    # """
    #        清除工作簿 wb 中，所有 NamedStyle.name 中包含 style_name 子串的样式
    #        """
