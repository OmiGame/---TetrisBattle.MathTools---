"""
路径配置文件
用于统一管理项目路径和导入配置
"""

import os
import sys

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 添加项目根目录到Python路径
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# 其他路径相关配置可以在这里添加 