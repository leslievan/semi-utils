import os

import yaml
from PIL import Image
from PIL import ImageFont


class ElementConfig(object):
    """
    布局中元素的配置对象
    """

    def __init__(self, element):
        self.element = element

    def get_name(self):
        return self.element['name']

    def is_bold(self):
        return self.element['is_bold']

    def get_value(self):
        return self.element['value'] if 'value' in self.element else None


# 字体大小，影响字体的清晰度
FONT_SIZE = 240
BOLD_FONT_SIZE = 260


class Config(object):
    """
    配置对象
    """

    def __init__(self, path):
        self.path = path
        with open(self.path, 'r', encoding='utf-8') as f:
            self._data = yaml.safe_load(f)
        self._logos = {}
        self._left_top = ElementConfig(self._data['layout']['elements']['left_top'])
        self._left_bottom = ElementConfig(self._data['layout']['elements']['left_bottom'])
        self._right_top = ElementConfig(self._data['layout']['elements']['right_top'])
        self._right_bottom = ElementConfig(self._data['layout']['elements']['right_bottom'])
        self.font = ImageFont.truetype(self._data['base']['font'], self._data['base']['font_size'])
        self.bold_font = ImageFont.truetype(self._data['base']['bold_font'], self._data['base']['bold_font_size'])
        self.makes = self._data['logo']['makes']

    def load_logo(self, make) -> Image.Image:
        """
        根据厂商获取 logo
        :param make: 厂商
        :return: logo
        """
        # 已经读到内存中的 logo
        if make in self._logos:
            return self._logos[make]
        # 未读取到内存中的 logo
        for m in self.makes.values():
            if m['id'].lower() in make.lower():
                logo = Image.open(m['path'])
                self._logos[make] = logo
                return logo

    def get(self) -> dict:
        return self._data

    def get_layout_type(self) -> str:
        return self._data['layout']['type']

    def get_left_top(self) -> ElementConfig:
        return self._left_top

    def get_left_bottom(self) -> ElementConfig:
        return self._left_bottom

    def get_right_top(self) -> ElementConfig:
        return self._right_top

    def get_right_bottom(self) -> ElementConfig:
        return self._right_bottom

    def save(self):
        with open(self.path, 'w') as f:
            yaml.dump(self._data, f, encoding='utf-8')

    def enable_shadow(self):
        self._data['global']['shadow']['enable'] = True

    def disable_shadow(self):
        self._data['global']['shadow']['enable'] = False

    def is_shadow_enable(self):
        return self._data['global']['shadow']['enable']

    def is_logo_enable(self):
        return self._data['logo']['enable']

    def is_logo_left(self):
        if self._data['logo']['position'] == 'left':
            return True

    def set_logo_left(self):
        self._data['logo']['position'] = 'left'

    def unset_logo_left(self):
        self._data['logo']['position'] = 'right'

    def is_white_margin_enable(self):
        return self._data['layout']['white_margin']['enable']

    def get_white_margin_width(self) -> int:
        white_margin_width = self._data['layout']['white_margin']['width']
        if white_margin_width > 30:
            white_margin_width = 30
        if white_margin_width < 0:
            white_margin_width = 0
        self._data['layout']['white_margin']['width'] = white_margin_width
        return white_margin_width

    def get_input_dir(self):
        return self._data['base']['input_dir']

    def get_output_dir(self):
        output_dir = self._data['base']['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir

    def get_quality(self):
        return self._data['base']['quality']

    def get_font(self):
        return self.font

    def get_bold_font(self):
        return self.bold_font

    def set_normal_layout(self):
        self._data['layout']['type'] = 'normal'

    def set_normal_with_right_logo_layout(self):
        self._data['layout']['type'] = 'normal_with_right_logo'
        self.unset_logo_left()

    def set_square_layout(self):
        self._data['layout']['type'] = 'square'

    def set_normal_with_original_ratio_layout(self):
        self._data['layout']['type'] = 'normal_with_original_ratio'

    def set_normal_with_right_logo_and_original_ratio_layout(self):
        self._data['layout']['type'] = 'normal_with_right_logo_and_original_ratio'

    def set_logo_enable(self):
        self._data['logo']['enable'] = True

    def set_logo_disable(self):
        self._data['logo']['enable'] = False

    def set_white_margin_enable(self):
        self._data['layout']['white_margin']['enable'] = True

    def set_white_margin_disable(self):
        self._data['layout']['white_margin']['enable'] = False

    def set_use_equivalent_focal_length_enable(self):
        self._data['param']['focal_length']['use_equivalent_focal_length'] = True

    def set_use_equivalent_focal_length_disable(self):
        self._data['param']['focal_length']['use_equivalent_focal_length'] = False

    def set_model(self, location):
        self._data['layout']['elements'][location]['name'] = 'Model'

    def set_left_top_model(self):
        self.set_model('left_top')

    def set_left_bottom_model(self):
        self.set_model('left_bottom')

    def set_right_top_model(self):
        self.set_model('right_top')

    def set_right_bottom_model(self):
        self.set_model('right_bottom')

    def set_make(self, location):
        self._data['layout']['elements'][location]['name'] = 'Make'

    def set_left_top_make(self):
        self.set_make('left_top')

    def set_left_bottom_make(self):
        self.set_make('left_bottom')

    def set_right_top_make(self):
        self.set_make('right_top')

    def set_right_bottom_make(self):
        self.set_make('right_bottom')

    def set_lens(self, location):
        self._data['layout']['elements'][location]['name'] = 'LensModel'

    def set_left_top_lens(self):
        self.set_lens('left_top')

    def set_left_bottom_lens(self):
        self.set_lens('left_bottom')

    def set_right_top_lens(self):
        self.set_lens('right_top')

    def set_right_bottom_lens(self):
        self.set_lens('right_bottom')

    def set_param(self, location):
        self._data['layout']['elements'][location]['name'] = 'Param'

    def set_left_top_param(self):
        self.set_param('left_top')

    def set_left_bottom_param(self):
        self.set_param('left_bottom')

    def set_right_top_param(self):
        self.set_param('right_top')

    def set_right_bottom_param(self):
        self.set_param('right_bottom')

    def set_datetime(self, location):
        self._data['layout']['elements'][location]['name'] = 'Datetime'

    def set_left_top_datetime(self):
        self.set_datetime('left_top')

    def set_left_bottom_datetime(self):
        self.set_datetime('left_bottom')

    def set_right_top_datetime(self):
        self.set_datetime('right_top')

    def set_right_bottom_datetime(self):
        self.set_datetime('right_bottom')

    def set_date(self, location):
        self._data['layout']['elements'][location]['name'] = 'Date'

    def set_left_top_date(self):
        self.set_date('left_top')

    def set_left_bottom_date(self):
        self.set_date('left_bottom')

    def set_right_top_date(self):
        self.set_date('right_top')

    def set_right_bottom_date(self):
        self.set_date('right_bottom')

    def set_custom(self, location):
        self._data['layout']['elements'][location]['name'] = 'Custom'
        user_input = input('输入自定义字段的值：\n')
        self._data['layout']['elements'][location]['value'] = user_input

    def set_left_top_custom(self):
        self.set_custom('left_top')

    def set_left_bottom_custom(self):
        self.set_custom('left_bottom')

    def set_right_top_custom(self):
        self.set_custom('right_top')

    def set_right_bottom_custom(self):
        self.set_custom('right_bottom')

    def set_none(self, location):
        self._data['layout']['elements'][location]['name'] = 'None'

    def set_left_top_none(self):
        self.set_none('left_top')

    def set_left_bottom_none(self):
        self.set_none('left_bottom')

    def set_right_top_none(self):
        self.set_none('right_top')

    def set_right_bottom_none(self):
        self.set_none('right_bottom')

    def use_equivalent_focal_length(self):
        return self._data['param']['focal_length']['use_equivalent_focal_length']
