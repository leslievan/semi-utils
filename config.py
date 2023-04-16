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
        self.left_top = Element(elements['left_top']['name'],
                                elements['left_top']['is_bold'],
                                elements['left_top']['value'] if 'value' in elements['left_top'] else None)
        self.left_bottom = Element(elements['left_bottom']['name'],
                                   elements['left_bottom']['is_bold'],
                                   elements['left_bottom']['value'] if 'value' in elements['left_bottom'] else None)
        self.right_top = Element(elements['right_top']['name'],
                                 elements['right_top']['is_bold'],
                                 elements['right_top']['value'] if 'value' in elements['right_top'] else None)
        self.right_bottom = Element(elements['right_bottom']['name'],
                                    elements['right_bottom']['is_bold'],
                                    elements['right_bottom']['value'] if 'value' in elements['right_bottom'] else None)
        self.type = layout['type']


# 布局，全局配置
FONT_SIZE = 240


def save_config():
    global config
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, encoding='utf-8')


def load_config():
    global logo_enable
    logo_enable = config['logo']['enable']


def get_logo(make):
    """
    根据厂商获取 logo
    :param make:
    :return:
    """
    if make in logos:
        return logos[make]
    for m in makes.values():
        if m['id'].lower() in make.lower():
            logo = Image.open(m['path'])
            logos[make] = logo
            return logo


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

white_margin_enable = config['layout']['white_margin']['enable']
white_margin_width = config['layout']['white_margin']['width']
if white_margin_width > 30:
    white_margin_width = 30
if white_margin_width < 0:
    white_margin_width = 0

def set_normal_layout():
    config['layout']['type'] = 'normal'


def set_normal_with_right_logo_layout():
    config['layout']['type'] = 'normal_with_right_logo'


def set_square_layout():
    config['layout']['type'] = 'square'


def set_logo_enable():
    config['logo']['enable'] = True


def set_logo_disable():
    config['logo']['enable'] = False


def set_white_margin_enable():
    config['layout']['white_margin']['enable'] = True


def set_white_margin_disable():
    config['layout']['white_margin']['enable'] = False


def set_use_equivalent_focal_length_enable():
    config['param']['focal_length']['use_equivalent_focal_length'] = True


def set_use_equivalent_focal_length_disable():
    config['param']['focal_length']['use_equivalent_focal_length'] = False


def set_model(location):
    config['layout']['elements'][location]['name'] = 'Model'


def set_left_top_model():
    set_model('left_top')


def set_left_bottom_model():
    set_model('left_bottom')


def set_right_top_model():
    set_model('right_top')


def set_right_bottom_model():
    set_model('right_bottom')


def set_make(location):
    config['layout']['elements'][location]['name'] = 'Make'


def set_left_top_make():
    set_make('left_top')


def set_left_bottom_make():
    set_make('left_bottom')


def set_right_top_make():
    set_make('right_top')


def set_right_bottom_make():
    set_make('right_bottom')


def set_lens(location):
    config['layout']['elements'][location]['name'] = 'Lens'


def set_left_top_lens():
    set_lens('left_top')


def set_left_bottom_lens():
    set_lens('left_bottom')


def set_right_top_lens():
    set_lens('right_top')


def set_right_bottom_lens():
    set_lens('right_bottom')


def set_param(location):
    config['layout']['elements'][location]['name'] = 'Param'


def set_left_top_param():
    set_param('left_top')


def set_left_bottom_param():
    set_param('left_bottom')


def set_right_top_param():
    set_param('right_top')


def set_right_bottom_param():
    set_param('right_bottom')


def set_date(location):
    config['layout']['elements'][location]['name'] = 'Date'


def set_left_top_date():
    set_date('left_top')


def set_left_bottom_date():
    set_date('left_bottom')


def set_right_top_date():
    set_date('right_top')


def set_right_bottom_date():
    set_date('right_bottom')


def set_custom(location):
    config['layout']['elements'][location]['name'] = 'Custom'
    user_input = input('输入自定义字段的值：\n')
    config['layout']['elements'][location]['value'] = user_input


def set_left_top_custom():
    set_custom('left_top')


def set_left_bottom_custom():
    set_custom('left_bottom')


def set_right_top_custom():
    set_custom('right_top')


def set_right_bottom_custom():
    set_custom('right_bottom')


def set_none(location):
    config['layout']['elements'][location]['name'] = 'None'


def set_left_top_none():
    set_none('left_top')


def set_left_bottom_none():
    set_none('left_bottom')


def set_right_top_none():
    set_none('right_top')


def set_right_bottom_none():
    set_none('right_bottom')
