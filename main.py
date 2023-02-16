import configparser
import math
import os
from datetime import datetime
from enum import Enum

from PIL import Image, ImageDraw
from PIL import ImageFont
from PIL.ExifTags import TAGS
from PIL.Image import Transpose


# 品牌枚举
class Make(Enum):
    NIKON = 'NIKON'
    CANON = 'CANON'
    SONY = 'SONY'


# 读取 exif 信息，包括相机机型、相机品牌、图片尺寸、镜头焦距、光圈大小、曝光时间、ISO 和拍摄时间
def get_exif(image):
    _exif_attrs = {'Model', 'Make', 'ExifImageWidth', 'ExifImageHeight', 'FocalLength', 'FNumber', 'ExposureTime',
                   'DateTimeOriginal', 'ISOSpeedRatings', 'Orientation'}
    _exif = {}
    info = image._getexif()
    if info:
        for attr, value in info.items():
            decoded_attr = TAGS.get(attr, attr)
            if decoded_attr in _exif_attrs:
                _exif[decoded_attr] = value

    return _exif


# 修改日期格式
def parse_datetime(datetime_string):
    return datetime.strptime(datetime_string, '%Y:%m:%d %H:%M:%S')


# 添加 logo
def append_logo(exif_img, make):
    logo = None
    if make == Make.NIKON:
        logo = Image.open(nikon_logo_path)
    elif make == Make.CANON:
        logo = Image.open(canon_logo_path)
    elif make == Make.SONY:
        logo = Image.open(sony_logo_path)
    if logo is not None:
        logo = logo.resize((exif_img.height, exif_img.height), Image.Resampling.LANCZOS)
        exif_img.paste(logo, (0, 0))


# 匹配相机品牌
def get_brand(make):
    for name, member in Make.__members__.items():
        if name in make:
            return member


# 生成元信息图片
def make_exif_image(exif):
    font_ratio = .07
    all_ratio = .13
    original_width = exif['ExifImageWidth']
    original_height = exif['ExifImageHeight']
    original_ratio = original_width / original_height
    if original_ratio > 1:
        font_ratio = .07
        all_ratio = .1

    # 型号
    model = exif['Model']
    make = exif['Make']
    model_mask = bold_font.getmask(model)
    make_mask = font.getmask(make)
    brand_img = Image.new('RGB',
                          (max(model_mask.size[0], make_mask.size[0]),
                           model_mask.size[1] + make_mask.size[1] + GAP_PIXEL * 3),
                          color='white')
    brand_draw = ImageDraw.Draw(brand_img)
    brand_draw.text((0, 0), model, font=bold_font, fill='black')
    brand_draw.text((0, model_mask.size[1] + GAP_PIXEL), make, font=font, fill='gray')

    # 参数
    focal_length = str(int(exif['FocalLength'])) + 'mm'
    f_number = 'F' + str(exif['FNumber'])
    exposure_time = str(exif['ExposureTime'].real)
    iso = 'ISO' + str(exif['ISOSpeedRatings'])
    shot_param = '  '.join((focal_length, f_number, exposure_time, iso))

    original_date_time = datetime.strftime(parse_datetime(exif['DateTimeOriginal']), '%Y-%m-%d %H:%M')
    shot_param_mask = bold_font.getmask(shot_param)
    original_date_time_mask = font.getmask(original_date_time)

    shot_param_img = Image.new('RGB',
                               (max(shot_param_mask.size[0], original_date_time_mask.size[0]),
                                shot_param_mask.size[1] + original_date_time_mask.size[1] + GAP_PIXEL * 3),
                               color='white')

    shot_param_draw = ImageDraw.Draw(shot_param_img)
    shot_param_draw.text((0, 0), shot_param, font=bold_font, fill='black')
    shot_param_draw.text((0, shot_param_mask.size[1] + GAP_PIXEL), original_date_time, font=font, fill='gray')

    exif_img = Image.new('RGB', (original_width, math.floor(all_ratio * original_width)), color='white')
    left_margin = BORDER_PIXEL
    right_margin = BORDER_PIXEL

    brand_img = brand_img.resize(
        (math.floor(brand_img.width / brand_img.height * math.floor(original_width * font_ratio)),
         math.floor(original_width * font_ratio)), Image.Resampling.LANCZOS)
    shot_param_img = shot_param_img.resize(
        (math.floor(shot_param_img.width / shot_param_img.height * math.floor(original_width * font_ratio)),
         math.floor(original_width * font_ratio)), Image.Resampling.LANCZOS)
    if logo_enable:
        append_logo(exif_img, get_brand(make))
        left_margin += exif_img.height
    exif_img.paste(brand_img, (left_margin, math.floor((all_ratio - font_ratio) / 2 * original_width)))
    exif_img.paste(shot_param_img, (exif_img.width - shot_param_img.width - right_margin,
                                    math.floor((all_ratio - font_ratio) / 2 * original_width)))

    return exif_img.resize((original_width, math.floor(all_ratio * original_width)), Image.Resampling.LANCZOS)


# 拼接原图片和 exif 图片
def concat_image(img_x, img_y):
    img = Image.new('RGB', (img_x.width, img_x.height + img_y.height), color='white')
    img.paste(img_x, (0, 0))
    img.paste(img_y, (0, img_x.height))
    return img


# 读取文件列表
def get_file_list():
    file_list = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if 'jpg' in file or 'jpeg' in file or 'JPG' in file or 'JPEG' in file:
                file_list.append(file)
    return file_list


# 布局
FONT_SIZE = 240
BORDER_PIXEL = 60
UP_DOWN_MARGIN = FONT_SIZE + BORDER_PIXEL
LEFT_RIGHT_MARGIN = FONT_SIZE + BORDER_PIXEL
GAP_PIXEL = 90

# 读取配置
con = configparser.ConfigParser()
con.read('./config.ini', encoding='utf-8')

# 读取输入、输出配置
input_dir = con.get('base', 'input_dir')
output_dir = con.get('base', 'output_dir')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
quality = con.getint('base', 'quality')

# 读取字体配置
font = ImageFont.truetype(con.get('base', 'font'), FONT_SIZE)
bold_font = ImageFont.truetype(con.get('base', 'bold_font'), FONT_SIZE)

# 读取 logo 配置
logo_enable = con.getboolean('logo', 'enable')
nikon_logo_path = con.get('logo', 'nikon')
canon_logo_path = con.get('logo', 'canon')
sony_logo_path = con.get('logo', 'sony')

if __name__ == '__main__':
    file_list = get_file_list()
    for file in file_list:
        # 打开图片
        img = Image.open(os.path.join(input_dir, file))
        # 生成 exif 图片
        exif = get_exif(img)
        if 'Orientation' in exif:
            if exif['Orientation'] == 3:
                img = img.transpose(Transpose.ROTATE_180)
                # exif['ExifImageWidth'], exif['ExifImageHeight'] = img.width, img.height
            elif exif['Orientation'] == 6:
                img = img.transpose(Transpose.ROTATE_270)
                # exif['ExifImageWidth'], exif['ExifImageHeight'] = exif['ExifImageHeight'], exif['ExifImageWidth']
            elif exif['Orientation'] == 8:
                img = img.transpose(Transpose.ROTATE_90)
                # exif['ExifImageWidth'], exif['ExifImageHeight'] = exif['ExifImageHeight'], exif['ExifImageWidth']
        exif['ExifImageWidth'], exif['ExifImageHeight'] = img.width, img.height
        exif_img = make_exif_image(exif)
        # 拼接两张图片
        cnt_img = concat_image(img, exif_img)
        cnt_img.save(os.path.join(output_dir, file), quality=quality)
