"""简单的图表查看工具 - 用于快速查看生成的经济系统图表"""
import os
import subprocess
import sys
from typing import List

def 获取图表文件列表(图表目录: str = "图表输出") -> List[str]:
    """获取图表文件列表
    
    Args:
        图表目录: 图表文件目录
        
    Returns:
        list: 图表文件路径列表
    """
    if not os.path.exists(图表目录):
        return []
    
    图表文件 = []
    for 文件名 in os.listdir(图表目录):
        if 文件名.endswith('.png'):
            图表文件.append(os.path.join(图表目录, 文件名))
    
    return sorted(图表文件)

def 打开图片文件(文件路径: str):
    """使用系统默认程序打开图片文件
    
    Args:
        文件路径: 图片文件路径
    """
    try:
        if sys.platform.startswith('win'):
            os.startfile(文件路径)
        elif sys.platform.startswith('darwin'):
            subprocess.call(['open', 文件路径])
        else:
            subprocess.call(['xdg-open', 文件路径])
        print(f"已打开图表: {os.path.basename(文件路径)}")
    except Exception as e:
        print(f"无法打开文件 {文件路径}: {e}")

def 打开图表文件夹(图表目录: str = "图表输出"):
    """打开图表文件夹
    
    Args:
        图表目录: 图表文件目录
    """
    try:
        if os.path.exists(图表目录):
            if sys.platform.startswith('win'):
                os.startfile(图表目录)
            elif sys.platform.startswith('darwin'):
                subprocess.call(['open', 图表目录])
            else:
                subprocess.call(['xdg-open', 图表目录])
            print(f"已打开图表文件夹: {图表目录}")
        else:
            print(f"图表目录不存在: {图表目录}")
    except Exception as e:
        print(f"无法打开文件夹: {e}")

def 显示图表菜单():
    """显示图表查看菜单"""
    图表目录 = "图表输出"
    
    while True:
        print("\n" + "=" * 60)
        print("经济系统图表查看器")
        print("=" * 60)
        
        # 获取图表文件列表
        图表文件列表 = 获取图表文件列表(图表目录)
        
        if not 图表文件列表:
            print("暂无可查看的图表文件。")
            print("\n可用操作:")
            print("1. 生成新图表")
            print("2. 打开图表文件夹")
            print("0. 退出")
        else:
            print("可查看的图表:")
            for i, 文件路径 in enumerate(图表文件列表, 1):
                文件名 = os.path.basename(文件路径)
                显示名 = 文件名.replace('.png', '').replace('_', ' ')
                print(f"{i}. {显示名}")
            
            print("\n其他操作:")
            print(f"{len(图表文件列表) + 1}. 查看所有图表")
            print(f"{len(图表文件列表) + 2}. 生成新图表")
            print(f"{len(图表文件列表) + 3}. 打开图表文件夹")
            print("0. 退出")
        
        print("-" * 60)
        
        try:
            选择 = input("请选择要执行的操作 (输入数字): ").strip()
            
            if 选择 == "0":
                print("退出图表查看器。")
                break
            elif 选择 == "":
                continue
            
            选择数字 = int(选择)
            
            if not 图表文件列表:
                # 没有图表文件时的操作
                if 选择数字 == 1:
                    生成新图表()
                elif 选择数字 == 2:
                    打开图表文件夹(图表目录)
                else:
                    print("无效的选择，请重新输入。")
            else:
                # 有图表文件时的操作
                if 1 <= 选择数字 <= len(图表文件列表):
                    # 打开单个图表
                    选中文件 = 图表文件列表[选择数字 - 1]
                    打开图片文件(选中文件)
                elif 选择数字 == len(图表文件列表) + 1:
                    # 查看所有图表
                    print("正在打开所有图表...")
                    for 文件路径 in 图表文件列表:
                        打开图片文件(文件路径)
                elif 选择数字 == len(图表文件列表) + 2:
                    # 生成新图表
                    生成新图表()
                elif 选择数字 == len(图表文件列表) + 3:
                    # 打开图表文件夹
                    打开图表文件夹(图表目录)
                else:
                    print("无效的选择，请重新输入。")
                    
        except ValueError:
            print("请输入有效的数字。")
        except KeyboardInterrupt:
            print("\n\n用户中断，退出程序。")
            break
        except Exception as e:
            print(f"发生错误: {e}")

def 生成新图表():
    """生成新的图表"""
    try:
        print("\n正在生成新图表，请稍候...")
        from EconomySystem.Diagrams import 生成所有资源图表
        
        生成的文件 = 生成所有资源图表()
        
        print(f"\n✓ 成功生成 {len(生成的文件)} 个图表文件:")
        for 文件路径 in 生成的文件:
            print(f"  - {os.path.basename(文件路径)}")
        
        input("\n按回车键继续...")
        
    except Exception as e:
        print(f"\n✗ 生成图表时发生错误: {e}")
        input("\n按回车键继续...")

def 显示帮助信息():
    """显示帮助信息"""
    print("""
经济系统图表查看器使用说明:

生成的图表类型:
1. 绿色碎片累积对比图 - 显示绿色碎片的产出与需求累积对比
2. 蓝色碎片累积对比图 - 显示蓝色碎片的产出与需求累积对比  
3. 紫色碎片累积对比图 - 显示紫色碎片的产出与需求累积对比
4. 金币累积对比图 - 显示金币的产出与需求累积对比
5. 资源累积综合对比图 - 所有资源的综合对比视图
6. 资源差值分析图 - 产出与需求的差值分析

图表说明:
- 实线表示累积产出
- 虚线表示累积需求  
- 绿色区域表示产出盈余
- 红色区域表示产出不足
- 差值图显示各资源的盈余/不足趋势

操作说明:
- 选择数字来查看对应图表
- 图表会用系统默认程序打开
- 可以同时打开多个图表进行对比
""")

if __name__ == "__main__":
    print("启动经济系统图表查看器...")
    
    # 检查是否需要先生成图表
    if not os.path.exists("图表输出") or not 获取图表文件列表():
        print("\n检测到暂无图表文件，是否先生成图表？")
        回答 = input("输入 y 生成图表，或直接回车进入主菜单: ").strip().lower()
        if 回答 in ['y', 'yes', '是']:
            生成新图表()
    
    # 显示主菜单
    显示图表菜单() 