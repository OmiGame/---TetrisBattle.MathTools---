"""Boss数据生成器，Boss数据比较简单，就直接生成表格了"""

import os
from ExcelTools import 表格工具
from Style.StyleDefiner import 表格样式类型
from MonsterData.MonsterDataManager import 怪物数据保存器
from MonsterData.MonsterTypes import 已设计怪物, 地图类型
from BossData.BossDataType import 战斗Boss, 技能Boss, Boss配置

class Boss生成器:
    def __init__(self, save_folder: str = None):
        """初始化Boss生成器
        
        Args:
            save_folder: 保存Excel文件的文件夹路径
        """
        self.save_folder = save_folder or r"H:\悠手好闲\铁头工作室\方块项目设计案\《冲王》数值_cursor\新数据生成"
        self.特殊行数 = 3  # 前3行是特殊行（##var, ##type, ##）
        self.特殊列数 = 1  # 第1列是特殊列

    def 生成战斗型Boss表格(self, 血量倍数: float = None, 攻击力倍数: float = None, 
                     表格样式: 表格样式类型 = 表格样式类型.默认样式) -> None:
        """生成战斗型Boss的表格
        
        Args:
            血量倍数: Boss血量的倍数，如果为None则使用默认配置
            攻击力倍数: Boss攻击力的倍数，如果为None则使用默认配置
            表格样式: 表格的样式类型
        """
        # 使用默认配置或传入的配置
        血量倍数 = 血量倍数 or Boss配置.战斗型Boss默认血量倍数
        攻击力倍数 = 攻击力倍数 or Boss配置.战斗型Boss默认攻击力倍数

        # 初始化保存路径和文件名
        os.makedirs(self.save_folder, exist_ok=True)
        file_path = os.path.join(self.save_folder, "#战斗型Boss属性表_3导.xlsx")
        sheet_name = "战斗型Boss属性"
        
        print(f"\n开始生成战斗型Boss属性表...")

        #为了让boss编号和怪物编号不冲突，给boss编号附加一个值
        Boss编号附加值 = 1000
        
        # 初始化怪物管理器，加载所有已保存怪物数据
        怪物管理器 = 怪物数据保存器()
        
        # 获取工作表对象和样式
        wb, ws, 表头样式名, 数据样式名 = 表格工具.更新或创建工作表(
            file_path, sheet_name, 表格样式
        )
        
        # 写入特殊的第一列数据
        for i in range(self.特殊行数):
            ws.cell(row=i+1, column=1, value=f"##{'var' if i==0 else 'type' if i==1 else ''}").style = 表头样式名
        
        # 获取列函数映射（使用怪物基础数据表的列函数映射）
        from TableData import 怪物基础数据表
        column_functions = 怪物基础数据表.获取列函数映射()
        
        # 从列函数映射中提取表头
        headers = {列定义.列名: 列定义.表头数据类型 for _, 列定义 in column_functions.items()}
        
        # 添加新的属性到表头
        headers.update({
            "移动速度": "float",
            "适配地图": "string",
            "对塔伤害": "int"
        })
        
        # 生成表头
        表格工具.生成表头(ws, headers, 表头样式名, start_row=1, start_col=self.特殊列数+1)
        
        # 遍历所有已设计的怪物，每个Boss只取一级数据
        当前行号 = self.特殊行数 + 1
        
        for 怪物枚举 in 已设计怪物:
            怪物名称 = 怪物枚举.value
            print(f"\n正在添加{怪物名称}的Boss数据...")
            
            # 创建行参数
            row_params = 怪物基础数据表.创建行参数(ws, 怪物名称, 1, 当前行号)
            
            # 创建列名到列号的映射
            列号映射 = {列名: 列号 for 列号, 列名 in enumerate(headers, self.特殊列数+1)}
            
            # 生成每列数据
            for col_num, 列定义 in column_functions.items():
                实际参数 = {映射键: row_params[实际键] for 映射键, 实际键 in 列定义.参数映射.items()}
                
                # 计算并写入单元格值
                raw_value = 列定义.计算值(实际参数, ws, 当前行号, 列号映射, self.特殊行数+1)
                
                # 对血量和攻击力应用倍数
                if "血量" in 列定义.列名:
                    raw_value *= 血量倍数
                elif "攻击力" in 列定义.列名:
                    raw_value *= 攻击力倍数
                elif "怪物编号" in 列定义.列名:
                    raw_value = raw_value + Boss编号附加值
                # 确保值是基本类型
                if isinstance(raw_value, (int, float)):
                    cell_value = round(float(raw_value), 1)
                else:
                    cell_value = str(raw_value)
                
                cell = ws.cell(row=当前行号, column=col_num + self.特殊列数, value=cell_value)
                cell.style = 数据样式名
            
            # 写入新增的属性
            ws.cell(row=当前行号, column=列号映射["移动速度"], value=row_params.get("移动速度", 1.2)).style = 数据样式名
            ws.cell(row=当前行号, column=列号映射["适配地图"], value=",".join([地图.value for 地图 in row_params.get("适配地图", [])])).style = 数据样式名
            ws.cell(row=当前行号, column=列号映射["对塔伤害"], value=20).style = 数据样式名
            
            当前行号 += 1
        
        # 调整列宽并保存文件
        表格工具.按中文调整列宽(ws, self.特殊行数, self.特殊列数+1, len(headers) + self.特殊列数)
        wb.save(file_path)
        print(f"\n战斗型Boss属性表生成完成，文件已保存至：{file_path}")

    def 生成技能型Boss表格(self, boss列表: list[技能Boss], 
                     表格样式: 表格样式类型 = 表格样式类型.默认样式) -> None:
        """生成技能型Boss的表格
        
        Args:
            boss列表: 技能型Boss的列表
            表格样式: 表格的样式类型
        """
        # 初始化保存路径和文件名
        os.makedirs(self.save_folder, exist_ok=True)
        file_path = os.path.join(self.save_folder, "#技能型Boss属性表_3导.xlsx")
        sheet_name = "技能型Boss属性"
        
        print(f"\n开始生成技能型Boss属性表...")
        
        # 获取工作表对象和样式
        wb, ws, 表头样式名, 数据样式名 = 表格工具.更新或创建工作表(
            file_path, sheet_name, 表格样式
        )
        
        # 写入特殊的第一列数据
        for i in range(self.特殊行数):
            ws.cell(row=i+1, column=1, value=f"##{'var' if i==0 else 'type' if i==1 else ''}").style = 表头样式名
        
        # 定义表头
        headers = {
            "名称": "string",
            "编号": "string",
            "技能等级": "int",
            "血量": "float",
            "移动速度": "float",
            "适配地图": "string",
            "对塔伤害": "int"
        }
        
        # 生成表头
        表格工具.生成表头(ws, headers, 表头样式名, start_row=1, start_col=self.特殊列数+1)
        
        # 写入数据
        当前行号 = self.特殊行数 + 1
        
        for boss in boss列表:
            # 写入每个字段
            ws.cell(row=当前行号, column=self.特殊列数+1, value=boss.名称).style = 数据样式名
            ws.cell(row=当前行号, column=self.特殊列数+2, value=boss.编号).style = 数据样式名
            ws.cell(row=当前行号, column=self.特殊列数+3, value=boss.技能等级).style = 数据样式名
            ws.cell(row=当前行号, column=self.特殊列数+4, value=round(boss.血量, 1)).style = 数据样式名
            ws.cell(row=当前行号, column=self.特殊列数+5, value=boss.移动速度).style = 数据样式名
            # 确保适配地图数据正确写入
            适配地图值 = ",".join(boss.适配地图) if boss.适配地图 else ""
            ws.cell(row=当前行号, column=self.特殊列数+6, value=适配地图值).style = 数据样式名
            ws.cell(row=当前行号, column=self.特殊列数+7, value=boss.对塔伤害).style = 数据样式名
            
            当前行号 += 1
        
        # 调整列宽并保存文件
        表格工具.按中文调整列宽(ws, self.特殊行数, self.特殊列数+1, len(headers) + self.特殊列数)
        wb.save(file_path)
        print(f"\n技能型Boss属性表生成完成，文件已保存至：{file_path}")

# 使用示例
if __name__ == "__main__":
    # 创建Boss生成器实例
    boss生成器 = Boss生成器()
    
    # 生成战斗型Boss表格（使用默认配置）
    boss生成器.生成战斗型Boss表格()
    
    # 生成技能型Boss表格（使用配置中的Boss列表）
    boss生成器.生成技能型Boss表格(Boss配置.技能型Boss列表)
