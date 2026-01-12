"""
共享类型定义
此文件不应依赖任何具体的 processor 实现，避免循环导入
"""
from enum import Enum


class Direction(Enum):
    """拼接方向"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    DIAGONAL = "diagonal"
    RADIAL = "radial"


class Alignment(Enum):
    """对齐方式"""
    # 通用
    START = "start"
    CENTER = "center"
    END = "end"

    # 语义化别名（水平拼接时的垂直对齐）
    TOP = "start"
    MIDDLE = "center"
    BOTTOM = "end"

    # 语义化别名（垂直拼接时的水平对齐）
    LEFT = "start"
    RIGHT = "end"
