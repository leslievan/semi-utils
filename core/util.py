import io
import platform
import re
import shutil
import subprocess
import time
from functools import wraps
from pathlib import Path

from PIL import Image

from core.logger import logger

if platform.system() == 'Windows':
    EXIFTOOL_PATH = Path('./exiftool/exiftool.exe')
    ENCODING = 'gbk'
elif shutil.which('exiftool') is not None:
    EXIFTOOL_PATH = shutil.which('exiftool')
    ENCODING = 'utf-8'
else:
    EXIFTOOL_PATH = Path('./exiftool/exiftool')
    ENCODING = 'utf-8'


def get_exif(path) -> dict:
    """
    获取exif信息
    :param path: 照片路径
    :return: exif信息
    """
    exif_dict = {}
    try:
        output_bytes = subprocess.check_output([EXIFTOOL_PATH, '-d', '%Y-%m-%d %H:%M:%S%3f%z', path])
        output = output_bytes.decode('utf-8', errors='ignore')

        lines = output.splitlines()
        utf8_lines = [line for line in lines]

        for line in utf8_lines:
            # 将每一行按冒号分隔成键值对
            kv_pair = line.split(':')
            if len(kv_pair) < 2:
                continue
            key = kv_pair[0].strip()
            value = ':'.join(kv_pair[1:]).strip()
            # 将键中的空格移除
            key = re.sub(r'\s+', '', key)
            key = re.sub(r'/', '', key)
            # 将键值对添加到字典中
            exif_dict[key] = value
        for key, value in exif_dict.items():
            # 过滤非 ASCII 字符
            value_clean = ''.join(c for c in value if ord(c) < 128)
            # 将处理后的值更新到 exif_dict 中
            exif_dict[key] = value_clean
    except Exception as e:
        logger.error(f'get_exif error: {path} : {e}')

    return exif_dict


def list_files(path: str, suffixes: set[str], depth: int = 0, max_depth: int = 20):
    """
    使用 pathlib 实现的版本

    Args:
        path: 要扫描的路径
        suffixes: 支持的文件后缀
        depth: 当前递归深度（内部使用）
        max_depth: 最大递归深度，防止无限递归
    """
    result = []
    root = Path(path).resolve()

    if not root.exists():
        return result

    # 防止递归过深
    if depth > max_depth:
        logger.warning(f"list_files: 达到最大递归深度 {max_depth}，跳过 {path}")
        return result

    try:
        # 分离文件夹和文件，分别排序
        items = list(root.iterdir())
        dirs = sorted([i for i in items if i.is_dir()], key=lambda x: x.name.lower(), reverse=True)
        files = sorted([i for i in items if i.is_file()], key=lambda x: (x.stat().st_mtime, x.name.lower()),
                       reverse=True)

        # 先处理文件夹
        for item in dirs:
            if item.name.startswith('.'):
                continue
            # 跳过符号链接，避免无限递归
            if item.is_symlink():
                continue
            children = list_files(str(item), suffixes, depth + 1, max_depth)
            if children:
                result.append({
                    'label': item.name,
                    'value': str(item),
                    'children': children,
                })

        # 再处理文件
        for item in files:
            if item.name.startswith('.'):
                continue
            if item.suffix.lower() in suffixes:
                result.append({
                    'label': item.name,
                    'value': str(item),
                    'is_file': True
                })

    except PermissionError:
        logger.debug(f"list_files: 权限不足，跳过 {path}")
    except Exception as e:
        logger.error(f"list_files: 扫描失败 {path}: {e}")

    return result


def log_rt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 调用被装饰的函数
        end_time = time.time()  # 记录结束时间
        elapsed_time = (end_time - start_time) * 1000  # 计算运行时间

        logger.debug(f"[monitor]api#{func.__name__} cost {elapsed_time:.2f}ms")
        return result

    return wrapper


def convert_heic_to_jpeg(path: str, quality: int = 90) -> io.BytesIO:
    """转换 HEIC 为 JPEG 字节流"""
    with Image.open(path) as img:
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality)
        buffer.seek(0)
        return buffer
