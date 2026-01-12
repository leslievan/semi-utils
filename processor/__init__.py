import importlib

import pillow_heif

from core.logger import logger
from processor import core


def _auto_register_processors():
    """
    自动发现并注册所有处理器
    扫描 processor 包下的所有模块，导入它们以触发 __init_subclass__ 钩子
    """
    # 需要扫描的模块列表
    modules_to_scan = [
        'processor.filters',
        'processor.generators',
        'processor.mergers',
    ]

    for module_name in modules_to_scan:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            logger.warning(f"Failed to import {module_name}: {e}")


def _get_all_processor_classes():
    """获取所有已注册的处理器类（用于验证）"""
    return core.get_all_processors()


# 自动注册所有处理器
_auto_register_processors()

# 注册 pillow heic 支持
pillow_heif.register_heif_opener()
logger.debug("Registered plugin: pillow_heif")
