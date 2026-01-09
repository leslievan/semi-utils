import sys
import os
from loguru import logger

# --- 配置常量 ---
# 日志文件存放路径
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志轮转配置: 每天 0 点生成新文件，或者文件超过 500MB 时生成新文件
ROTATION = "00:00"
# ROTATION = "500 MB"

# 日志保留配置: 只保留最近 10 天的日志
RETENTION = "10 days"

# 日志压缩格式
COMPRESSION = "zip"

# 定义日志格式 (如果你需要 JSON 格式以便 ELK 采集，loguru 也有 serialize=True 选项)
# 这个格式包含了：时间、日志级别、模块名、函数名、行号、具体信息
FORMAT_CONSOLE = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
FORMAT_FILE = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}.{function}:{line} - {message}"

def setup_logging(debug: bool = False):
    """
    配置 loguru 日志系统
    :param debug: 是否开启 Debug 模式
    """
    # 1. 移除 loguru 默认的 handler (避免重复输出，且我们可以自定义 level)
    logger.remove()

    # 2. 确定日志级别
    log_level = "DEBUG" if debug else "INFO"

    # 3. 添加控制台输出 Handler (开发、Docker环境看)
    logger.add(
        sys.stderr,
        level=log_level,
        format=FORMAT_CONSOLE,
        colorize=True,
        backtrace=True,  # 详细的异常追踪
        diagnose=True    # 异常诊断（生产环境为了安全可设为 False）
    )

    # 4. 添加普通业务日志文件 Handler
    logger.add(
        os.path.join(LOG_DIR, "app.log"),
        level="INFO",
        format=FORMAT_FILE,
        rotation=ROTATION,
        retention=RETENTION,
        compression=COMPRESSION,
        encoding="utf-8",
        enqueue=True,  # 异步写入，线程安全，且性能更好
        backtrace=True,
        diagnose=True
    )

    # 5. (可选) 它可以单独把 ERROR 级别的日志剥离到 error.log，方便报警监控
    logger.add(
        os.path.join(LOG_DIR, "error.log"),
        level="ERROR",
        format=FORMAT_FILE,
        rotation=ROTATION,
        retention=RETENTION,
        encoding="utf-8",
        enqueue=True,
    )

    return logger

# --- 初始化 (通常在程序入口调用，或者直接 import 这个实例) ---
# 默认初始化一次，项目中直接 import { logger } from ... 即可
llogger = setup_logging(debug=True)

