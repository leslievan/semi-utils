import os
import platform
import re
import subprocess

import piexif
from PIL import Image
from PIL.ExifTags import TAGS

if platform.system() == 'Windows':
    exiftool_path = './exiftool/exiftool.exe'
else:
    exiftool_path = './exiftool/exiftool'


def get_file_list(path):
    """
    获取 jpg 文件列表
    :param path: 路径
    :return: 文件名
    """
    file_list = [file for file in os.listdir(path) if
                 'jpg' in file or 'jpeg' in file or 'JPG' in file or 'JPEG' in file]
    return file_list


def get_exif(path) -> dict:
    """
    获取exif信息
    :param path: 照片路径
    :return: exif信息
    """
    output = subprocess.check_output([exiftool_path, path])
    exif_dict = {}
    for line in output.splitlines():
        # 将每一行按冒号分隔成键值对
        line = line.decode('utf-8')  # 将 bytes 转换为 str
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

    _exif = {}
    with Image.open(path) as image:
        info = image._getexif()
        if info:
            for attr, value in info.items():
                decoded_attr = TAGS.get(attr, attr)
                _exif[decoded_attr] = value

    if 'LensModel' in exif_dict:
        _exif['LensModel'] = exif_dict['LensModel']
    elif 'Lens' in exif_dict:
        _exif['LensModel'] = exif_dict['Lens']
    elif 'LensID' in exif_dict:
        _exif['LensModel'] = exif_dict['LensID']
    return _exif


def copy_exif_data(source_path, target_path) -> None:
    """
    复制照片的 exif 信息
    :param source_path: 原始照片路径
    :param target_path: 目的照片路径
    """
    try:
        # 读取源照片的 exif 信息
        src_exif = piexif.load(source_path)

        # 将 exif 信息转换为字节串
        src_exif_bytes = piexif.dump(src_exif)

        # 将源照片的 exif 信息写入 target_path
        piexif.insert(src_exif_bytes, target_path)

    except ValueError:
        print("错误：{} exif 信息复制失败".format(source_path))
