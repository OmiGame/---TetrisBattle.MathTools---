"""图表查看器 - 用于查看生成的经济系统图表"""
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.image as mpimg

class 图表查看器:
    """图表查看器GUI应用
    
    用于浏览和查看生成的经济系统分析图表
    """
    
    def __init__(self):
        """初始化图表查看器"""
        self.root = tk.Tk()
        self.root.title("经济系统图表查看器")
        self.root.geometry("1200x800")
        
        self.图表目录 = "图表输出"
        self.当前图表路径 = None
        
        self.创建界面()
        self.加载图表列表()
        
    def 创建界面(self):
        """创建用户界面"""
        # 创建主框架
        主框架 = ttk.Frame(self.root)
        主框架.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        控制面板 = ttk.Frame(主框架, width=250)
        控制面板.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        控制面板.pack_propagate(False)
        
        # 图表列表
        ttk.Label(控制面板, text="图表列表", font=("微软雅黑", 12, "bold")).pack(pady=(0, 10))
        
        # 图表列表框
        列表框架 = ttk.Frame(控制面板)
        列表框架.pack(fill=tk.BOTH, expand=True)
        
        self.图表列表 = tk.Listbox(列表框架, font=("微软雅黑", 10))
        滚动条 = ttk.Scrollbar(列表框架, orient=tk.VERTICAL, command=self.图表列表.yview)
        self.图表列表.config(yscrollcommand=滚动条.set)
        
        self.图表列表.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.图表列表.bind('<<ListboxSelect>>', self.选择图表)
        
        # 按钮框架
        按钮框架 = ttk.Frame(控制面板)
        按钮框架.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(按钮框架, text="刷新列表", command=self.加载图表列表).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(按钮框架, text="重新生成图表", command=self.重新生成图表).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(按钮框架, text="打开图表文件夹", command=self.打开图表文件夹).pack(fill=tk.X)
        
        # 右侧图表显示区域
        图表框架 = ttk.Frame(主框架)
        图表框架.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 图表标题
        self.图表标题 = ttk.Label(图表框架, text="请选择图表", font=("微软雅黑", 14, "bold"))
        self.图表标题.pack(pady=(0, 10))
        
        # 图表显示标签
        self.图表显示标签 = ttk.Label(图表框架, text="暂无图表", 
                                 justify=tk.CENTER, font=("微软雅黑", 12))
        self.图表显示标签.pack(expand=True)
        
    def 加载图表列表(self):
        """加载图表文件列表"""
        self.图表列表.delete(0, tk.END)
        
        if not os.path.exists(self.图表目录):
            self.图表列表.insert(tk.END, "图表目录不存在")
            return
            
        图表文件 = [f for f in os.listdir(self.图表目录) if f.endswith('.png')]
        
        if not 图表文件:
            self.图表列表.insert(tk.END, "暂无图表文件")
            return
            
        for 文件名 in sorted(图表文件):
            # 去掉.png后缀显示
            显示名称 = 文件名[:-4]
            self.图表列表.insert(tk.END, 显示名称)
    
    def 选择图表(self, event):
        """选择图表事件处理"""
        selection = self.图表列表.curselection()
        if not selection:
            return
            
        选中项 = self.图表列表.get(selection[0])
        if 选中项 in ["图表目录不存在", "暂无图表文件"]:
            return
            
        图表文件名 = 选中项 + ".png"
        图表路径 = os.path.join(self.图表目录, 图表文件名)
        
        if os.path.exists(图表路径):
            self.显示图表(图表路径, 选中项)
        else:
            self.图表标题.config(text="文件不存在")
            self.图表显示标签.config(text="所选图表文件不存在", image="")
    
    def 显示图表(self, 图表路径: str, 图表名称: str):
        """显示选中的图表"""
        try:
            # 更新标题
            self.图表标题.config(text=图表名称)
            
            # 加载图片
            image = Image.open(图表路径)
            
            # 计算合适的显示尺寸
            显示区域宽度 = 900
            显示区域高度 = 600
            
            # 保持宽高比缩放
            原始宽度, 原始高度 = image.size
            宽度比 = 显示区域宽度 / 原始宽度
            高度比 = 显示区域高度 / 原始高度
            缩放比 = min(宽度比, 高度比, 1.0)  # 不放大，只缩小
            
            新宽度 = int(原始宽度 * 缩放比)
            新高度 = int(原始高度 * 缩放比)
            
            # 调整图片大小
            image = image.resize((新宽度, 新高度), Image.Resampling.LANCZOS)
            
            # 转换为tkinter可用的格式
            photo = ImageTk.PhotoImage(image)
            
            # 显示图片
            self.图表显示标签.config(image=photo, text="")
            self.图表显示标签.image = photo  # 保持引用
            
            self.当前图表路径 = 图表路径
            
        except Exception as e:
            self.图表标题.config(text="图表加载失败")
            self.图表显示标签.config(text=f"加载图表时发生错误:\n{str(e)}", image="")
            self.图表显示标签.image = None
    
    def 重新生成图表(self):
        """重新生成图表"""
        try:
            # 显示正在生成的提示
            self.图表标题.config(text="正在重新生成图表...")
            self.图表显示标签.config(text="请稍候，正在生成图表...", image="")
            self.root.update()
            
            # 导入并运行图表生成模块
            from EconomySystem.Diagrams import 生成所有资源图表
            生成的文件 = 生成所有资源图表(self.图表目录)
            
            # 刷新列表
            self.加载图表列表()
            
            # 显示成功消息
            self.图表标题.config(text="图表生成完成")
            成功消息 = f"成功生成 {len(生成的文件)} 个图表文件:\n\n"
            成功消息 += "\n".join([os.path.basename(f) for f in 生成的文件])
            self.图表显示标签.config(text=成功消息, image="")
            
        except Exception as e:
            self.图表标题.config(text="图表生成失败")
            self.图表显示标签.config(text=f"生成图表时发生错误:\n{str(e)}", image="")
    
    def 打开图表文件夹(self):
        """打开图表文件夹"""
        try:
            import subprocess
            import sys
            
            if os.path.exists(self.图表目录):
                if sys.platform.startswith('win'):
                    os.startfile(self.图表目录)
                elif sys.platform.startswith('darwin'):
                    subprocess.call(['open', self.图表目录])
                else:
                    subprocess.call(['xdg-open', self.图表目录])
            else:
                tk.messagebox.showwarning("警告", f"图表目录不存在: {self.图表目录}")
                
        except Exception as e:
            tk.messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")
    
    def 运行(self):
        """启动图表查看器"""
        self.root.mainloop()

def 启动图表查看器():
    """启动图表查看器应用"""
    try:
        app = 图表查看器()
        app.运行()
    except Exception as e:
        print(f"启动图表查看器时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    启动图表查看器() 