import os

import yaml
from PIL import ImageFont, Image


class Element(object):
    def __init__(self, name, is_bold, value=None):
        self.name = name
        self.is_bold = is_bold
        self.value = value


class Layout(object):
    def __init__(self, layout):
        elements = layout['elements']
        self.left1 = Element(elements['left1']['id'],
                             elements['left1']['is_bold'],
                             elements['left1']['value'] if 'value' in elements['left1'] else None)
        self.left2 = Element(elements['left2']['id'],
                             elements['left2']['is_bold'],
                             elements['left2']['value'] if 'value' in elements['left2'] else None)
        self.right1 = Element(elements['right1']['id'],
                              elements['right1']['is_bold'],
                              elements['right1']['value'] if 'value' in elements['right1'] else None)
        self.right2 = Element(elements['right2']['id'],
                              elements['right2']['is_bold'],
                              elements['right2']['value'] if 'value' in elements['right2'] else None)
        self.type = layout['type']


# 布局，全局配置
FONT_SIZE = 240
BORDER_PIXEL = 60
UP_DOWN_MARGIN = FONT_SIZE + BORDER_PIXEL
LEFT_RIGHT_MARGIN = FONT_SIZE + BORDER_PIXEL
GAP_PIXEL = 90

# 读取配置
with open('config.yaml', 'r', encoding='utf-8') as f:
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
empty_logo = Image.new('RGB', (1000, 1000), color='white')
logos = {}


def get_logo(make):
    """
    根据厂商获取 logo
    :param make:
    :return:
    """
    if make in logos:
        return logos[make]
    for m in makes.values():
        if m['id'] in make:
            logo = Image.open(m['path'])
            logos[make] = logo
            return logo


white_margin_enable = config['layout']['white_margin']['enable']
white_margin_width = config['layout']['white_margin']['width']
if white_margin_width > 30:
    white_margin_width = 30
if white_margin_width < 0:
    white_margin_width = 0
