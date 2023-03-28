import os

import piexif
from PIL.ExifTags import TAGS


def get_file_list(path):
    """
    获取文件列表
    :param path: 路径
    :return: 文件名
    """
    file_list = [file for file in os.listdir(path) if
                 'jpg' in file or 'jpeg' in file or 'JPG' in file or 'JPEG' in file]
    return file_list


def get_exif(image):
    """
    获取exif信息
    :param image:
    :return:
    """
    _exif = {}
    info = image._getexif()
    if info:
        for attr, value in info.items():
            decoded_attr = TAGS.get(attr, attr)
            _exif[decoded_attr] = value

    return _exif


def copy_exif_data(source_path, target_path):
    # 读取源照片的 exif 信息
    src_exif = piexif.load(source_path)
    # 将 exif 信息转换为字节串
    src_exif_bytes = piexif.dump(src_exif)

    # 将源照片的 exif 信息写入 target_path
    piexif.insert(src_exif_bytes, target_path)
