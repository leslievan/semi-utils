import math
import os

import yaml
from PIL import Image, ImageDraw
from PIL import ImageFont
from PIL.Image import Transpose

from utils import parse_datetime, get_file_list, concat_img, get_exif, get_str_from_exif

# 布局，全局配置
FONT_SIZE = 240
BORDER_PIXEL = 60
UP_DOWN_MARGIN = FONT_SIZE + BORDER_PIXEL
LEFT_RIGHT_MARGIN = FONT_SIZE + BORDER_PIXEL
GAP_PIXEL = 90

# 读取配置
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 读取输入、输出配置
input_dir = config['base']['input_dir']
output_dir = config['base']['output_dir']
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
quality = config['base']['quality']

# 读取字体配置
font = ImageFont.truetype(config['base']['font'], FONT_SIZE)
bold_font = ImageFont.truetype(config['base']['bold_font'], FONT_SIZE)

# 读取 logo 配置
logo_enable = config['logo']['enable']
makes = config['logo']['makes']


# 添加 logo
def append_logo(exif_img, exif):
    logo = None
    if 'Make' in exif:
        make = exif['Make']
        for m in makes.values():
            if m['id'] in make:
                logo = Image.open(m['path'])
    if logo is not None:
        logo = logo.resize((exif_img.height, exif_img.height), Image.Resampling.LANCZOS)
        exif_img.paste(logo, (0, 0))


def append_logo2(img):
    logo = Image.open('./logos/static_logo.png')
    logo = logo.resize((math.floor(img.height * 1.25), img.height), Image.Resampling.LANCZOS)
    new_img = Image.new('RGB', (img.width + logo.width, img.height), color='white')
    new_img.paste(logo, (0, 0))
    new_img.paste(img, (logo.width, 0))
    return new_img


def make_two_line_img(first, second, color='white'):
    mask_first = bold_font.getmask(first)
    mask_second = font.getmask(second)
    m1_width = mask_first.size[0] if first != '' else bold_font.getmask('A').size[0]
    m2_width = mask_second.size[0] if second != '' else font.getmask('A').size[0]
    m1_height = mask_first.size[1] if first != '' else bold_font.getmask('A').size[1]
    m2_height = mask_second.size[1] if second != '' else font.getmask('A').size[1]
    _img = Image.new('RGB', (max(m1_width, m2_width), m1_height + m2_height + GAP_PIXEL * 3), color=color)
    draw = ImageDraw.Draw(_img)
    draw.text((0, 0), first, font=bold_font, fill='black')
    draw.text((0, m1_height + GAP_PIXEL), second, font=font, fill='gray')
    return _img


def make_normal_watermark(exif, infos):
    original_width, original_height = infos['original_width'], infos['original_height']
    all_ratio, font_ratio = infos['all_ratio'], infos['font_ratio']
    # 位置 1
    c_11 = get_str_from_exif(exif, elements[0])
    c_12 = get_str_from_exif(exif, elements[1])
    img_1 = make_two_line_img(c_11, c_12)

    # 位置 2
    c_21 = get_str_from_exif(exif, elements[2])
    c_22 = get_str_from_exif(exif, elements[3])
    img_2 = make_two_line_img(c_21, c_22)

    img_watermark = Image.new('RGB', (original_width, math.floor(all_ratio * original_width)), color='white')
    left_margin = BORDER_PIXEL
    right_margin = BORDER_PIXEL

    # 根据照片长缩放水印元素
    img_1_x_length = math.floor(img_1.width / img_1.height * math.floor(original_width * font_ratio))
    img_2_x_length = math.floor(img_2.width / img_2.height * math.floor(original_width * font_ratio))
    img_1_y_length = math.floor(original_width * font_ratio)
    img_2_y_length = math.floor(original_width * font_ratio)
    img_1 = img_1.resize((img_1_x_length, img_1_y_length), Image.Resampling.LANCZOS)
    img_2 = img_2.resize((img_2_x_length, img_2_y_length), Image.Resampling.LANCZOS)

    # 是否添加 logo
    if layout == 'normal_with_right_logo':
        img_2 = append_logo2(img_2)
    elif logo_enable:
        append_logo(img_watermark, exif)
        # 计算边界
        left_margin += img_watermark.height

    # 拼接元素 1 和元素 2
    img_watermark.paste(img_1, (left_margin, math.floor((all_ratio - font_ratio) / 2 * original_width)))
    img_watermark.paste(img_2, (
        img_watermark.width - img_2.width - right_margin, math.floor((all_ratio - font_ratio) / 2 * original_width)))

    return img_watermark


elements = config['layout']['elements']


# 生成元信息图片
def make_exif_img(exif, layout):
    # 修改水印长宽比
    font_ratio = .07
    all_ratio = .13
    original_width = exif['ExifImageWidth']
    original_height = exif['ExifImageHeight']
    original_ratio = original_width / original_height
    if original_ratio > 1:
        font_ratio = .07
        all_ratio = .1

    wm_x_length = original_width
    wm_y_length = math.floor(all_ratio * original_width)
    img_watermark = Image.new('RGB', (wm_x_length, wm_y_length))
    settings = {'original_width': original_width, 'original_height': original_height, 'all_ratio': all_ratio,
                'font_ratio': font_ratio}
    if layout == 'normal' or layout == 'normal_with_right_logo':
        img_watermark = make_normal_watermark(exif, settings)
    # 根据照片长缩放水印
    return img_watermark.resize((wm_x_length, wm_y_length), Image.Resampling.LANCZOS)


def add_white_frame(pil_img, frame_width):
    width, height = pil_img.size
    # create a blank image with wider canvas
    canvas = Image.new('RGB', (width + frame_width * 2, height + frame_width), color='white')
    # past the original image onto the blank canvas
    canvas.paste(pil_img, (frame_width, frame_width))
    return canvas


white_margin_enable = config['layout']['white_margin']['enable']
white_margin_width = config['layout']['white_margin']['width']
if white_margin_width > 30:
    white_margin_width = 30
if white_margin_width < 0:
    white_margin_width = 0

if __name__ == '__main__':
    file_list = get_file_list(input_dir)
    layout = config['layout']['type']
    for file in file_list:
        # 打开图片
        img = Image.open(os.path.join(input_dir, file))
        # 生成 exif 图片
        exif = get_exif(img)
        # 修复图片方向
        if 'Orientation' in exif:
            if exif['Orientation'] == 3:
                img = img.transpose(Transpose.ROTATE_180)
            elif exif['Orientation'] == 6:
                img = img.transpose(Transpose.ROTATE_270)
            elif exif['Orientation'] == 8:
                img = img.transpose(Transpose.ROTATE_90)
        exif['ExifImageWidth'], exif['ExifImageHeight'] = img.width, img.height

        exif_img = make_exif_img(exif, layout)
        # 拼接两张图片
        cnt_img = concat_img(img, exif_img)
        if white_margin_enable:
            cnt_img = add_white_frame(cnt_img, int(white_margin_width * img.width / 100))
        cnt_img.save(os.path.join(output_dir, file), quality=quality)
