"""
统一日志模块

使用 loguru 提供统一的日志接口，自动拦截 Flask 的标准 logging 输出
"""
import sys
import logging
from logging import DEBUG
from pathlib import Path
from loguru import logger

# 移除 loguru 默认的 handler
logger.remove()

# 默认配置（会被 setup_logging 覆盖）
DEFAULT_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"


class InterceptHandler(logging.Handler):
    """
    拦截标准 logging 的输出，重定向到 loguru

    这样 Flask、Werkzeug 等使用标准 logging 的库的日志也会被 loguru 处理
    """

    def emit(self, record):
        # 获取对应的 loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    rotation: str = "00:00",
    retention: str = "10 days",
    compression: str = "zip",
    enable_console: bool = True,
    enable_file: bool = True,
):
    """
    配置 loguru 日志系统

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_dir: 日志文件目录
        rotation: 日志轮转策略 (如 "00:00", "500 MB")
        retention: 日志保留时间 (如 "10 days")
        compression: 压缩格式 ("zip", "gz", "tar")
        enable_console: 是否输出到控制台
        enable_file: 是否输出到文件

    Returns:
        logger 实例
    """
    # 确保日志目录存在
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # 控制台输出
    if enable_console:
        logger.add(
            sys.stderr,
            level=log_level,
            format=DEFAULT_FORMAT,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    # 文件输出 - 所有日志
    if enable_file:
        logger.add(
            log_path / "app_{time:YYYY-MM-DD}.log",
            level="DEBUG",
            format=FILE_FORMAT,
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
            enqueue=True,  # 异步写入，线程安全
            backtrace=True,
            diagnose=True,
        )

        # 单独的错误日志
        logger.add(
            log_path / "error_{time:YYYY-MM-DD}.log",
            level="ERROR",
            format=FILE_FORMAT,
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
            enqueue=True,
        )

    # 拦截标准 logging（Flask、Werkzeug 等）
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 禁用 urllib3 的 verbose 日志
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger


def init_from_config(config):
    """
    从配置对象初始化日志系统

    Args:
        config: ConfigParser 对象
    """
    debug_mode = config.getboolean('DEFAULT', 'debug', fallback=False)
    log_level = "DEBUG" if debug_mode else "INFO"

    return setup_logging(log_level=log_level)


# 导出 logger
__all__ = ["logger", "setup_logging", "init_from_config"]