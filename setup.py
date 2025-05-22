"""setup.py 是 Python 项目的​​构建脚本​​，通常放在项目根目录下，用于定义项目的元数据（如名称、版本、依赖项等），并支持安装、打包和分发。"""
from setuptools import setup, find_packages

setup(
    name="chongwang",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openpyxl","pygame","numpy","matplotlib"
    ],
) 