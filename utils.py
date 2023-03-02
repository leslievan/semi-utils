import os

from PIL.ExifTags import TAGS


def get_file_list(path):
    """
    获取文件列表
    :param path: 路径
    :return: 文件名
    """
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if 'jpg' in file or 'jpeg' in file or 'JPG' in file or 'JPEG' in file:
                file_list.append(file)
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
