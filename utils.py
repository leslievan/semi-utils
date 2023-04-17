import platform
import re
import subprocess
from pathlib import Path

import piexif
from PIL import Image
from PIL.ExifTags import TAGS

if platform.system() == 'Windows':
    exiftool_path = './exiftool/exiftool.exe'
    encoding = 'gbk'
else:
    exiftool_path = './exiftool/exiftool'
    encoding = 'utf-8'


def get_file_list(path):
    """
    获取文件列表
    :param path: 路径
    :return: 文件名
    """
    path = Path(path)
    return [file_path for file_path in path.iterdir()
            if file_path.is_file() and file_path.suffix in ['.jpg', '.jpeg', '.JPG', '.JPEG']]


def get_exif(path):
    """
    获取exif信息
    :param path:
    :return:
    """

    _exif = {}
    with Image.open(path) as image:
        info = image._getexif()
        if info:
            for attr, value in info.items():
                decoded_attr = TAGS.get(attr, attr)
                _exif[decoded_attr] = value
    try:
        # 如果 exif 中不存在镜头信息，用 exiftool 读取
        if 'LensModel' not in _exif:
            output = subprocess.check_output([exiftool_path, '-charset', 'UTF8', path])

            output = output.decode(encoding)
            lines = output.splitlines()
            utf8_lines = [line for line in lines]

            exif_dict = {}
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
            if 'LensModel' in exif_dict:
                _exif['LensModel'] = exif_dict['LensModel']
            elif 'Lens' in exif_dict:
                _exif['LensModel'] = exif_dict['Lens']
            elif 'LensID' in exif_dict:
                _exif['LensModel'] = exif_dict['LensID']
    except UnicodeDecodeError as e:
        print('UnicodeDecodeError: {}'.format(path))
        pass
    finally:
        pass

    return _exif


def copy_exif_data(source_path, target_path):
    try:
        # 读取源照片的 exif 信息
        src_exif = piexif.load(str(source_path))

        # 将 exif 信息转换为字节串
        src_exif_bytes = piexif.dump(src_exif)

        # 将源照片的 exif 信息写入 target_path
        piexif.insert(src_exif_bytes, str(target_path))

    except ValueError:
        pass
