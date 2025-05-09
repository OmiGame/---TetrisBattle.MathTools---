import os
from typing import Type, Any, Dict
from ExcelTools import 表格工具
from Style.StyleDefiner import 表格样式类型
from TableData import 怪物基础数据表, 肉鸽技能节奏, 角色成长表, 阵容战力成长时间分布, 阵容战力成长表
from LubanData import 全局参数
from MonsterData.MonsterDataManager import 怪物数据保存器
from MonsterData.MonsterTypes import 已设计怪物
# 终端清屏，快速查看bug
os.system('cls' if os.name == 'nt' else 'clear')

# -------------------------------------
# 1. 定义全局变量
# -------------------------------------
# 保存文件夹的地址
save_folder_path = r"H:\悠手好闲\铁头工作室\方块项目设计案\《冲王》数值_cursor\新数据生成"

# 特殊行和特殊列的定义，这个项目是luban的导入的格式需要的
特殊行数 = 3  # 前3行是特殊行（##var, ##type, ##）
特殊列数 = 1  # 第1列是特殊列

# -------------------------------------
# 2. 生成表格的定义函数
# -------------------------------------
class 生成表:
    @classmethod
    def 从列函数映射提取表头(cls, 列函数映射: Dict[int, Any]) -> Dict[str, str]:
        """从列函数映射中提取表头信息
        
        Args:
            列函数映射: 列函数映射字典
            
        Returns:
            Dict[str, str]: 表头字典，键为列名，值为数据类型
        """
        表头字典 = {}
        for _, 列定义 in 列函数映射.items():
            # 列名作为表头字典的键
            列名 = 列定义.列名
            
            # 检查列名是否包含特殊符号，这部分逻辑来自表头信息类
            特殊符号 = "()（）/\\|<>{}[]【】《》"
            for 符号 in 特殊符号:
                if 符号 in 列名:
                    raise ValueError(f"表头显示名称 '{列名}' 不能包含特殊符号 '{符号}'")
            
            # 使用列定义中的表头数据类型
            表头字典[列名] = 列定义.表头数据类型
        return 表头字典

    @classmethod
    def 生成表格(cls, 表格定义: Type[Any], sheet_name: str = None, save_folder: str = None, 
                表格样式: 表格样式类型 = 表格样式类型.默认样式) -> None:
        """生成指定类型的表格
        根据表格定义类生成对应的Excel表格
        Args:
            表格定义: 表格定义类，包含表格的所有数据定义
            sheet_name: 工作表名称，如果为None则使用表格定义中的默认名称
            save_folder: 保存Excel文件的文件夹路径，如果为None则使用默认路径
            表格样式: 表格的样式类型
        """
        # 使用默认值
        if save_folder is None:
            save_folder = save_folder_path
        if sheet_name is None:
            sheet_name = 表格定义.默认工作表名称

        # 创建保存目录
        os.makedirs(save_folder, exist_ok=True)
        file_path = os.path.join(save_folder, 表格定义.表格名称)

        # 获取工作表对象和样式
        wb, ws, 表头样式名, 数据样式名 = 表格工具.更新或创建工作表(
            file_path, sheet_name, 表格样式
        )

        # 写入特殊的第一列数据
        for i in range(特殊行数):
            ws.cell(row=i+1, column=1, value=f"##{'var' if i==0 else 'type' if i==1 else ''}").style = 表头样式名

        # 获取列函数映射
        column_functions = 表格定义.获取列函数映射()
        
        # 从列函数映射中提取表头，而不是使用预定义的表头枚举
        headers = cls.从列函数映射提取表头(column_functions)
        
        # 生成表头，从特殊列之后开始
        表格工具.生成表头(ws, headers, 表头样式名, start_row=1, start_col=特殊列数+1)

        # 获取行数据范围
        起始值, 结束值 = 表格定义.获取行数据范围()

        # 生成数据行，从特殊行之后开始
        for 当前值 in range(起始值, 结束值 + 1):
            row_num = 当前值 - 起始值 + 特殊行数 + 1  # +1是因为行号从1开始
            
            # 创建行参数，等于创建了实际键的映射表
            row_params = 表格定义.创建行参数(ws, ws.title, 当前值, row_num)

            # 创建列名到列号的映射
            列号映射 = {列名: 列号 for 列号, 列名 in enumerate(headers, 特殊列数+1)}  # 从特殊列之后开始

            # 生成每列数据
            for col_num, 列定义 in column_functions.items():
                # 根据参数映射创建实际的参数字典，等于重新定义了字典
                实际参数 = {映射键: row_params[实际键] for 映射键, 实际键 in 列定义.参数映射.items()}
                
                # 计算并写入单元格值
                raw_value = 列定义.计算值(实际参数, ws, row_num, 列号映射, 特殊行数+1)  # 特殊行数+1是数据起始行号
                
                # 确保值是基本类型（字符串、数字等），而不是单元格对象
                if isinstance(raw_value, (int, float)):
                    cell_value = round(float(raw_value), 1)
                else:
                    cell_value = str(raw_value)
                
                cell = ws.cell(row=row_num, column=col_num + 特殊列数, value=cell_value)  # +特殊列数是因为前面有特殊列
                cell.style = 数据样式名

        # 调整列宽并保存文件
        表格工具.按中文调整列宽(ws, 特殊行数, 特殊列数+1, len(headers) + 特殊列数)  # 从特殊列之后开始
        wb.save(file_path)
        print(f"Excel文件已生成在：{file_path}")

    @classmethod
    def 将公式转换为值(cls, file_path: str) -> None:
        """将Excel文件中的所有公式转换为实际值"""
        from openpyxl import load_workbook
        # 加载工作簿，使用data_only=True来获取公式计算后的值
        wb = load_workbook(file_path, data_only=True)
        # 保存文件，这会覆盖原文件，但只包含值而不包含公式
        wb.save(file_path)
        print(f"已将公式转换为值：{file_path}")

    @classmethod
    def 生成所有等级的阵容战力成长时间分布表(cls, save_folder: str = save_folder_path, 
                                表格样式: 表格样式类型 = 表格样式类型.默认样式) -> None:
        """生成从1级到角色等级上限的所有等级的阵容战力成长时间分布表
        
        Args:
            save_folder: 保存Excel文件的文件夹路径，如果为None则使用默认路径
            表格样式: 表格的样式类型
        """
            
        # 从全局参数获取角色等级上限
        角色等级上限 = 全局参数.角色等级上限
        
        print(f"\n开始生成1级到{角色等级上限}级的阵容战力成长时间分布表...")
        
        # 循环生成每个等级的表格
        for 等级 in range(1, 角色等级上限 + 1):
            print(f"\n正在生成等级{等级}的阵容战力成长时间分布表...")
            cls.生成表格(
                表格定义=阵容战力成长时间分布,
                sheet_name=f"等级{等级}",
                save_folder=save_folder,
                表格样式=表格样式
            )
        
        print(f"\n所有等级(1-{角色等级上限})的阵容战力成长时间分布表生成完成!")

    @classmethod
    def 生成所有已设计怪物表格(cls, save_folder: str = save_folder_path, 
                            表格样式: 表格样式类型 = 表格样式类型.默认样式) -> None:
        """生成所有已设计怪物的表格
        
        Args:
            save_folder: 保存Excel文件的文件夹路径，如果为None则使用默认路径
            表格样式: 表格的样式类型
        """
            
        print(f"\n开始生成所有已设计怪物的表格...")
        
        # 初始化已生成怪物实例
        _ = 怪物数据保存器()  # 这会触发单例模式的初始化，初始化时加载保存的怪物数据
        
        # 遍历所有已设计的怪物
        for 怪物 in 已设计怪物:
            print(f"\n正在生成{怪物.value}的表格...")
            cls.生成表格(
                表格定义=怪物基础数据表,
                sheet_name=怪物.value,
                save_folder=save_folder,
                表格样式=表格样式
            )
        
        print(f"\n所有已设计怪物的表格生成完成!")

    @classmethod
    def 生成怪物初始属性汇总表(cls, save_folder: str = save_folder_path, 
                            表格样式: 表格样式类型 = 表格样式类型.默认样式) -> None:
        """生成所有怪物一级属性汇总表，将所有怪物的一级数据放在同一个表格的同一个sheet中
        
        Args:
            save_folder: 保存Excel文件的文件夹路径，如果为None则使用默认路径
            表格样式: 表格的样式类型
        """
        # 初始化保存路径和文件名
        os.makedirs(save_folder, exist_ok=True)
        file_path = os.path.join(save_folder, "#怪物初始属性汇总表_3导.xlsx")
        sheet_name = "怪物初始属性"
        
        print(f"\n开始生成怪物初始属性汇总表...")
        
        # 初始化已生成怪物实例
        怪物管理器 = 怪物数据保存器()  # 这会触发单例模式的初始化，初始化时加载保存的怪物数据
        
        # 获取工作表对象和样式
        wb, ws, 表头样式名, 数据样式名 = 表格工具.更新或创建工作表(
            file_path, sheet_name, 表格样式
        )
        
        # 写入特殊的第一列数据
        for i in range(特殊行数):
            ws.cell(row=i+1, column=1, value=f"##{'var' if i==0 else 'type' if i==1 else ''}").style = 表头样式名
        
        # 获取列函数映射
        column_functions = 怪物基础数据表.获取列函数映射()
        
        # 从列函数映射中提取表头
        headers = cls.从列函数映射提取表头(column_functions)
        
        # 生成表头，从特殊列之后开始
        表格工具.生成表头(ws, headers, 表头样式名, start_row=1, start_col=特殊列数+1)
        
        # 遍历所有已设计的怪物，每个怪物只取一级数据
        当前行号 = 特殊行数 + 1  # 从特殊行之后开始
        
        for 怪物枚举 in 已设计怪物:
            怪物名称 = 怪物枚举.value
            print(f"\n正在添加{怪物名称}的一级数据...")
            
            # 创建行参数
            row_params = 怪物基础数据表.创建行参数(ws, 怪物名称, 1, 当前行号)  # 1是怪物等级
            
            # 创建列名到列号的映射
            列号映射 = {列名: 列号 for 列号, 列名 in enumerate(headers, 特殊列数+1)}  # 从特殊列之后开始
            
            # 生成每列数据
            for col_num, 列定义 in column_functions.items():
                # 根据参数映射创建实际的参数字典
                实际参数 = {映射键: row_params[实际键] for 映射键, 实际键 in 列定义.参数映射.items()}
                
                # 计算并写入单元格值
                raw_value = 列定义.计算值(实际参数, ws, 当前行号, 列号映射, 特殊行数+1)
                
                # 确保值是基本类型（字符串、数字等），而不是单元格对象
                if isinstance(raw_value, (int, float)):
                    cell_value = round(float(raw_value), 1)
                else:
                    cell_value = str(raw_value)
                
                cell = ws.cell(row=当前行号, column=col_num + 特殊列数, value=cell_value)
                cell.style = 数据样式名
            
            当前行号 += 1
        
        # 调整列宽并保存文件
        表格工具.按中文调整列宽(ws, 特殊行数, 特殊列数+1, len(headers) + 特殊列数)
        wb.save(file_path)
        print(f"\n怪物初始属性汇总表生成完成，文件已保存至：{file_path}")

# 调用示例
if __name__ == "__main__":
    print("开始生成表格...")
    
    # # 生成角色表（使用角色成长表样式）
    # print("\n正在生成弓箭手表格...")
    # 生成表.生成表格(
    #     表格定义=角色成长表,
    #     sheet_name="弓箭手",
    #     save_folder=save_folder_path,
    #     表格样式=表格样式类型.角色成长表
    # )

    # # 生成士兵表（使用士兵表样式）
    # print("\n正在生成士兵表格...")
    # 生成表.生成表格(
    #     表格定义=角色成长表,
    #     sheet_name="士兵",
    #     save_folder=save_folder_path,
    #     表格样式=表格样式类型.角色成长表
    # )

    # print("\n正在生成士兵表格...")
    # 生成表.生成表格(
    #     表格定义=角色成长表,
    #     sheet_name="弓",
    #     save_folder=save_folder_path,
    #     表格样式=表格样式类型.角色成长表
    # )


    # print("\n正在生成阵容战力成长表...")
    # 生成表.生成表格(
    #     表格定义=阵容战力成长表,
    #     sheet_name="标准阵容列表",
    #     save_folder=save_folder_path,
    #     表格样式=表格样式类型.默认样式
    # )

    # 生成表.生成所有等级的阵容战力成长时间分布表()

    # 生成所有已设计怪物的表格
    生成表.生成所有已设计怪物表格()
    
    # 生成怪物初始属性汇总表
    生成表.生成怪物初始属性汇总表()
