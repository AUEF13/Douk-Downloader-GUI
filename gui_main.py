# DouK-Downloader GUI 启动脚本
# 使用方法:
#     1. 安装 Python 3.12: 已安装至 C:\tool\Python312
#     2. 安装依赖: C:\tool\Python312\python.exe -m pip install PySide6 qasync
#     3. 运行: C:\tool\Python312\python.exe gui_main.py
import sys
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("错误: 未安装 PySide6")
    print("请运行: C:\\tool\\Python312\\python.exe -m pip install PySide6 qasync")
    sys.exit(1)

from src.gui_edition import run_gui

if __name__ == "__main__":
    run_gui()
