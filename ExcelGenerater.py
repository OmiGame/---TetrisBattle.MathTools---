import os
from typing import Type, Any
from ExcelTools import 表格工具
from LubanData import 全局参数
from Style.StyleDefiner import 表格样式类型
from TableData import 角色成长表, 阵容战力成长表

# 终端清屏，快速查看bug
os.system('cls' if os.name == 'nt' else 'clear')

# -------------------------------------
# 1. 定义全局变量
# -------------------------------------
# 保存文件夹的地址
save_folder_path = r"H:\悠手好闲\铁头工作室\方块项目设计案\《冲王》数值_cursor\图表生成"

# -------------------------------------
# 2. 生成表格的定义函数
# -------------------------------------
class 生成表:
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
            sheet_name = 表格定义.工作表名称

        # 创建保存目录
        os.makedirs(save_folder, exist_ok=True)
        file_path = os.path.join(save_folder, 表格定义.表格名称)

        # 获取工作表对象和样式
        wb, ws, 表头样式名, 数据样式名 = 表格工具.更新或创建工作表(
            file_path, sheet_name, 表格样式
        )

        # 生成表头，表头都是从第一行开始
        表格工具.生成表头(ws, 表格定义.headers, 表头样式名)

        # 获取列函数映射
        column_functions = 表格定义.获取列函数映射()

        # 获取行数据范围
        起始值, 结束值 = 表格定义.获取行数据范围()

        # 生成数据行，当前值为数据行的索引
        for 当前值 in range(起始值, 结束值 + 1):
            row_num = 当前值 - 起始值 + 2  # +2是因为第一行是表头
            
            # 创建行参数，等于创建了实际键的映射表
            row_params = 表格定义.创建行参数(ws, ws.title, 当前值, row_num)

            # 生成每列数据
            for col_num, 列定义 in column_functions.items():
                # 根据参数映射创建实际的参数字典，等于重新定义了字典
                实际参数 = {映射键: row_params[实际键] for 映射键, 实际键 in 列定义.参数映射.items()}
                
                # 计算并写入单元格值
                raw_value = 列定义.列函数(实际参数)
                # 确保值是基本类型（字符串、数字等），而不是单元格对象
                if isinstance(raw_value, (int, float)):
                    cell_value = round(float(raw_value), 1)
                else:
                    cell_value = str(raw_value)
                cell = ws.cell(row=row_num, column=col_num, value=cell_value)
                cell.style = 数据样式名

        # 调整列宽并保存文件
        表格工具.按中文调整列宽(ws, 1, 10)
        wb.save(file_path)
        print(f"Excel文件已生成在：{file_path}")

# 调用示例
if __name__ == "__main__":
    print("开始生成表格...")
    
    # 生成角色表（使用角色成长表样式）
    print("\n正在生成弓箭手表格...")
    生成表.生成表格(
        表格定义=角色成长表,
        sheet_name="弓箭手",
        save_folder=save_folder_path,
        表格样式=表格样式类型.角色成长表
    )

    # 生成士兵表（使用士兵表样式）
    print("\n正在生成士兵表格...")
    生成表.生成表格(
        表格定义=角色成长表,
        sheet_name="士兵",
        save_folder=save_folder_path,
        表格样式=表格样式类型.角色成长表
    )

    print("\n正在生成弓箭手表格...")
    生成表.生成表格(
        表格定义=角色成长表,
        sheet_name="弓箭手",
        save_folder=save_folder_path,
        表格样式=表格样式类型.角色成长表
    )

    print("\n正在生成弓箭手表格...")
    生成表.生成表格(
        表格定义=角色成长表,
        sheet_name="弓",
        save_folder=save_folder_path,
        表格样式=表格样式类型.角色成长表
    )

    print("\n正在生成阵容战力成长表...")
    生成表.生成表格(
        表格定义=阵容战力成长表,
        sheet_name="标准阵容列表",
        save_folder=save_folder_path,
        表格样式=表格样式类型.默认样式
    )
    
    
    print("\n正在生成阵容战力成长表...")
    生成表.生成表格(
        表格定义=阵容战力成长表,
        sheet_name="测试阵容列表",
        save_folder=save_folder_path,
        表格样式=表格样式类型.默认样式
    )



    
    print("\n所有表格生成完成！")
