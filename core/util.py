import io
import json
import os
import platform
import re
import shutil
import subprocess
import time
from functools import wraps
from pathlib import Path

from PIL import Image
from jinja2 import Template

from core.configs import templates_dir
from core.jinja2renders import vh, vw, auto_logo
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

        logger.info(f"[monitor]api#{func.__name__} cost {elapsed_time:.2f}ms")
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


# ==================== 模板管理相关方法 ====================

def get_template_path(template_name: str) -> Path:
    """
    获取模板文件的完整路径

    Args:
        template_name: 模板名称（不含扩展名），如 "standard1"

    Returns:
        模板文件的完整 Path 对象
    """
    return templates_dir / f"{template_name}.json"


def get_template(template_name: str) -> Template:
    """
    读取并解析模板文件为 Jinja2 Template 对象

    Args:
        template_name: 模板名称（不含扩展名），如 "standard1"

    Returns:
        Jinja2 Template 对象，已注册 vh, vw, auto_logo 全局函数
    """
    template_path = get_template_path(template_name)
    with open(template_path, encoding='utf-8') as f:
        template_str = f.read()
    template = Template(template_str)
    template.globals['vh'] = vh
    template.globals['vw'] = vw
    template.globals['auto_logo'] = auto_logo
    return template


def get_template_content(template_name: str) -> str:
    """
    获取模板文件的内容（原始字符串）

    Args:
        template_name: 模板名称（不含扩展名），如 "standard1"

    Returns:
        模板文件的原始内容字符串
    """
    template_path = get_template_path(template_name)
    with open(template_path, encoding='utf-8') as f:
        return f.read()


def save_template(template_name: str, content: str) -> None:
    """
    保存模板文件

    Args:
        template_name: 模板名称（不含扩展名），如 "standard1"
        content: 模板内容（JSON 字符串）
    """
    template_path = get_template_path(template_name)
    # 确保目录存在
    template_path.parent.mkdir(parents=True, exist_ok=True)
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_template(template_name: str, content: str = '[]') -> None:
    """
    创建新的模板文件

    Args:
        template_name: 模板名称（不含扩展名），如 "my_template"
        content: 模板内容（JSON 字符串），默认为空数组 '[]'

    Raises:
        FileExistsError: 如果模板文件已存在
    """
    template_path = get_template_path(template_name)
    if template_path.exists():
        raise FileExistsError(f"模板 '{template_name}' 已存在")
    save_template(template_name, content)


def list_templates() -> list[str]:
    """
    列出所有可用的模板名称

    Returns:
        模板名称列表（不含扩展名）
    """
    if not templates_dir.exists():
        return []
    return [f.stem for f in templates_dir.glob('*.json')]
