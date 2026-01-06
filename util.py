import platform
import re
import shutil
import subprocess
from pathlib import Path

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
