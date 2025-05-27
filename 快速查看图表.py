"""快速查看所有生成的经济系统图表"""
import os
import subprocess
import sys

def 打开所有图表():
    """打开所有生成的图表文件"""
    图表目录 = "图表输出"
    
    if not os.path.exists(图表目录):
        print(f"图表目录不存在: {图表目录}")
        return
    
    # 获取所有PNG文件
    图表文件 = [f for f in os.listdir(图表目录) if f.endswith('.png')]
    
    if not 图表文件:
        print("未找到图表文件，是否需要先生成图表？")
        回答 = input("输入 y 生成图表: ").strip().lower()
        if 回答 in ['y', 'yes', '是']:
            生成图表()
            return
        else:
            return
    
    print(f"找到 {len(图表文件)} 个图表文件:")
    for 文件名 in sorted(图表文件):
        print(f"  - {文件名}")
    
    print("\n正在打开图表...")
    
    # 打开每个图表文件
    for 文件名 in sorted(图表文件):
        文件路径 = os.path.join(图表目录, 文件名)
        try:
            if sys.platform.startswith('win'):
                os.startfile(文件路径)
            elif sys.platform.startswith('darwin'):
                subprocess.call(['open', 文件路径])
            else:
                subprocess.call(['xdg-open', 文件路径])
            print(f"✓ 已打开: {文件名}")
        except Exception as e:
            print(f"✗ 无法打开 {文件名}: {e}")
    
    print("\n所有图表已打开！")

def 生成图表():
    """生成所有图表"""
    try:
        print("\n正在生成图表，请稍候...")
        from EconomySystem.Diagrams import 生成所有资源图表
        
        生成的文件 = 生成所有资源图表()
        
        print(f"\n✓ 成功生成 {len(生成的文件)} 个图表文件:")
        for 文件路径 in 生成的文件:
            print(f"  - {os.path.basename(文件路径)}")
        
        print("\n正在打开所有图表...")
        打开所有图表()
        
    except Exception as e:
        print(f"\n✗ 生成图表时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("经济系统图表快速查看器")
    print("=" * 60)
    
    打开所有图表() 