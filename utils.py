import os
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
    获取 jpg 文件列表
    :param path: 路径
    :return: 文件名
    """
    path = Path(path)
    return [file_path for file_path in path.iterdir()
            if file_path.is_file() and file_path.suffix in ['.jpg', '.jpeg', '.JPG', '.JPEG']]


def get_exif(path) -> dict:
    """
    获取exif信息
    :param path: 照片路径
    :return: exif信息
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


def copy_exif_data(source_path, target_path) -> None:
    """
    复制照片的 exif 信息
    :param source_path: 原始照片路径
    :param target_path: 目的照片路径
    """
    try:
        # 读取源照片的 exif 信息
        src_exif = piexif.load(str(source_path))

        # 将 exif 信息转换为字节串
        src_exif_bytes = piexif.dump(src_exif)

        # 将源照片的 exif 信息写入 target_path
        piexif.insert(src_exif_bytes, str(target_path))

    except ValueError:
        pass


TINY_HEIGHT = 800


def remove_white_edge(image):
    """
    移除图片白边
    :param image: 图片对象
    :return: 移除白边后的图片对象
    """
    # 获取像素信息
    pixels = image.load()

    # 获取图像大小
    width, height = image.size

    # 计算最小的 X、Y、最大的 X、Y 坐标
    min_x, min_y = width - 1, height - 1
    max_x, max_y = 0, 0
    for y in range(height):
        for x in range(width):
            if pixels[x, y] != (255, 255, 255):
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    # 计算新的图像大小
    new_width = max_x - min_x + 1
    new_height = max_y - min_y + 1

    # 裁剪图像
    new_image = image.crop((min_x, min_y, max_x + 1, max_y + 1))
    return new_image


def concatenate_image(images, align='left'):
    """
    将多张图片拼接成一列
    :param images: 图片对象列表
    :param align: 对齐方向，left/center/right
    :return: 拼接后的图片对象
    """
    widths, heights = zip(*(i.size for i in images))

    sum_height = sum(heights)
    max_width = max(widths)

    new_img = Image.new('RGB', (max_width, sum_height), color='white')

    x_offset = 0
    y_offset = 0
    if 'left' == align:
        for img in images:
            new_img.paste(img, (0, y_offset))
            y_offset += img.height
    elif 'center' == align:
        for img in images:
            x_offset = int((max_width - img.width) / 2)
            new_img.paste(img, (x_offset, y_offset))
            y_offset += img.height
    elif 'right' == align:
        for img in images:
            x_offset = max_width - img.width  # 右对齐
            new_img.paste(img, (x_offset, y_offset))
            y_offset += img.height
    return new_img


def padding_image(image, padding_size, padding_location='tb'):
    """
    在图片四周填充白色像素
    :param image: 图片对象
    :param padding_size: 填充像素大小
    :param padding_location: 填充位置，top/bottom/left/right
    :return: 填充白色像素后的图片对象
    """
    if image is None:
        return None

    total_width, total_height = image.size
    x_offset, y_offset = 0, 0
    if 't' in padding_location:
        total_height += padding_size
        y_offset += padding_size
    if 'b' in padding_location:
        total_height += padding_size
    if 'l' in padding_location:
        total_width += padding_size
        x_offset += padding_size
    if 'r' in padding_location:
        total_width += padding_size

    padding_img = Image.new('RGB', (total_width, total_height), color='white')
    padding_img.paste(image, (x_offset, y_offset))
    return padding_img


def square_image(image):
    """
    将图片按照正方形进行填充
    :param image: 图片对象
    :return: 填充后的图片对象
    """
    # 计算图片的宽度和高度
    width, height = image.size

    # 计算需要填充的白色区域大小
    delta_w = abs(width - height)
    padding = (delta_w // 2, 0) if width < height else (0, delta_w // 2)

    # 创建新的正方形画布
    square_size = max(width, height)
    square_img = Image.new('RGB', (square_size, square_size), color='white')

    # 将输入的图片粘贴到正方形画布的中心位置
    square_img.paste(image, padding)

    # 返回正方形图片对象
    return square_img


def resize_image_with_height(image, height):
    """
    按照高度对图片进行缩放
    :param image: 图片对象
    :param height: 指定高度
    :return: 按照高度缩放后的图片对象
    """
    # 获取原始图片的宽度和高度
    width, old_height = image.size

    # 计算缩放后的宽度
    scale = height / old_height
    new_width = round(width * scale)

    # 进行等比缩放
    resized_image = image.resize((new_width, height), Image.ANTIALIAS)

    # 返回缩放后的图片对象
    return resized_image


def resize_image_with_width(image, width):
    """
    按照宽度对图片进行缩放
    :param image: 图片对象
    :param width: 指定宽度
    :return: 按照宽度缩放后的图片对象
    """
    # 获取原始图片的宽度和高度
    old_width, height = image.size

    # 计算缩放后的宽度
    scale = width / old_width
    new_height = round(height * scale)

    # 进行等比缩放
    resized_image = image.resize((width, new_height), Image.ANTIALIAS)

    # 返回缩放后的图片对象
    return resized_image


def append_image_by_side(background, images, side='left', padding=200, is_start=False):
    """
    将图片横向拼接到背景图片中
    :param background: 背景图片对象
    :param images: 图片对象列表
    :param side: 拼接方向，left/right
    :param padding: 图片之间的间距
    :param is_start: 是否在最左侧添加 padding
    :return: 拼接后的图片对象
    """
    if 'right' == side:
        if is_start:
            x_offset = background.width - padding
        else:
            x_offset = background.width
        images.reverse()
        for i in images:
            if i is None:
                continue
            i = resize_image_with_height(i, background.height)
            x_offset -= i.width
            x_offset -= padding
            background.paste(i, (x_offset, 0))
    else:
        if is_start:
            x_offset = padding
        else:
            x_offset = 0
        for i in images:
            if i is None:
                continue
            i = resize_image_with_height(i, background.height)
            background.paste(i, (x_offset, 0))
            x_offset += i.width
            x_offset += padding
