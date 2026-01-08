import platform
import re
import shutil
import subprocess
import time
from functools import wraps
from pathlib import Path

from jinja2 import pass_context

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
        print(f'get_exif error: {path} : {e}')

    return exif_dict


from pathlib import Path


def list_files(path: str, suffixes: set[str]):
    """
    使用 pathlib 实现的版本
    """
    result = []
    root = Path(path).resolve()

    if not root.exists():
        return result

    try:
        # 分离文件夹和文件，分别排序
        items = list(root.iterdir())
        dirs = sorted([i for i in items if i.is_dir()], key=lambda x: x.name.lower())
        files = sorted([i for i in items if i.is_file()], key=lambda x: x.name.lower())

        # 先处理文件夹
        for item in dirs:
            if item.name.startswith('.'):
                continue
            children = list_files(str(item), suffixes)
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
        pass

    return result


def log_rt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 调用被装饰的函数
        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算运行时间
        print(f"Function {func.__name__} took {elapsed_time:.6f} seconds to execute.")
        return result

    return wrapper


@pass_context
def vw(context, percent):
    """
    根据上下文中的 exif.ImageWidth 计算视口高度百分比对应的像素值
    :param context: Jinja2 模板上下文（类似字典）
    :param percent: 百分比数值（如 90 表示 90%）
    :return: 整数像素值
    """
    # 安全获取 exif.ImageWidth
    exif = context.get('exif', {})
    if hasattr(exif, 'get'):
        width = exif.get('ImageWidth', 0)
    else:
        # 支持对象形式（如 SimpleNamespace）
        width = getattr(exif, 'ImageWidth', 0)
    try:
        width = int(width)
    except (TypeError, ValueError):
        width = 0
    return int(width * percent / 100)


@pass_context
def vh(context, percent):
    """
    根据上下文中的 exif.ImageWidth 计算视口高度百分比对应的像素值
    :param context: Jinja2 模板上下文（类似字典）
    :param percent: 百分比数值（如 90 表示 90%）
    :return: 整数像素值
    """
    # 安全获取 exif.ImageWidth
    exif = context.get('exif', {})
    if hasattr(exif, 'get'):
        height = exif.get('ImageHeight', 0)
    else:
        # 支持对象形式（如 SimpleNamespace）
        height = getattr(exif, 'ImageHeight', 0)
    try:
        height = int(height)
    except (TypeError, ValueError):
        height = 0
    return int(height * percent / 100)
