import pillow_heif

from core.logger import logger
from processor import core


def _auto_register_processors():
    """
    自动发现并注册所有处理器
    使用直接导入以确保 PyInstaller 能正确打包
    """
    try:
        # 直接导入各处理器模块，PyInstaller 静态分析可以找到这些依赖
        from processor import filters, generators, mergers
        logger.debug("All processor modules imported successfully")
    except ImportError as e:
        logger.warning(f"Failed to import processor modules: {e}")


def _get_all_processor_classes():
    """获取所有已注册的处理器类（用于验证）"""
    return core.get_all_processors()


# 自动注册所有处理器
_auto_register_processors()

# 注册 pillow heic 支持
pillow_heif.register_heif_opener()
logger.debug("Registered plugin: pillow_heif")
