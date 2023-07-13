import os
from typing import Any
from typing import Type
from typing import TypeVar
from typing import cast

import yaml
from PIL import Image
from PIL import ImageFont

from enums.constant import CUSTOM_VALUE
from enums.constant import LOCATION_LEFT_BOTTOM
from enums.constant import LOCATION_LEFT_TOP
from enums.constant import LOCATION_RIGHT_BOTTOM
from enums.constant import LOCATION_RIGHT_TOP

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


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

    def get_color(self):
        if 'color' in self.element:
            return self.element['color']
        else:
            return '#212121'


class VideoConfig(object):
    resolution: str
    duration: str
    rate: int
    background_color: str
    background_music: str
    size: str

    def __init__(self, resolution: str, duration: str, rate: int, background_color: str,
                 background_music: str, size: str) -> None:
        self.resolution = resolution
        self.duration = duration
        self.rate = rate
        self.background_color = background_color
        self.background_music = background_music
        self.size = size

    @staticmethod
    def from_dict(obj: Any) -> 'VideoConfig':
        assert isinstance(obj, dict)
        resolution = from_str(obj.get("resolution"))
        duration = from_str(obj.get("duration"))
        rate = from_int(obj.get("rate"))
        background_color = from_str(obj.get("background_color"))
        background_music = from_str(obj.get("background_music"))
        size = from_str(obj.get("size"))
        return VideoConfig(resolution, duration, rate, background_color, background_music, size)

    def to_dict(self) -> dict:
        result: dict = {}
        result["resolution"] = from_str(self.resolution)
        result["duration"] = from_int(self.duration)
        result["rate"] = from_int(self.rate)
        result["background_color"] = from_str(self.background_color)
        result["background_music"] = from_str(self.background_music)
        result["size"] = from_str(self.size)
        return result


# 字体大小，影响字体的清晰度
FONT_SIZE = 240
BOLD_FONT_SIZE = 260


class Config(object):
    """
    配置对象
    """

    def __init__(self, path):
        self._path = path
        with open(self._path, 'r', encoding='utf-8') as f:
            self._data = yaml.safe_load(f)
        self._logos = {}
        self._left_top = ElementConfig(self._data['layout']['elements'][LOCATION_LEFT_TOP])
        self._left_bottom = ElementConfig(self._data['layout']['elements'][LOCATION_LEFT_BOTTOM])
        self._right_top = ElementConfig(self._data['layout']['elements'][LOCATION_RIGHT_TOP])
        self._right_bottom = ElementConfig(self._data['layout']['elements'][LOCATION_RIGHT_BOTTOM])
        self._makes = self._data['logo']['makes']
        self.bg_color = self._data['layout']['background_color'] \
            if 'background_color' in self._data['layout'] \
            else '#ffffff'
        self._video = VideoConfig.from_dict(self._data['video'])

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
        for m in self._makes.values():
            if m['id'].lower() in make.lower():
                logo = Image.open(m['path'])
                self._logos[make] = logo
                return logo

    def get(self) -> dict:
        return self._data

    def get_input_dir(self):
        return self._data['base']['input_dir']

    def get_output_dir(self):
        output_dir = self._data['base']['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir

    def get_quality(self):
        return self._data['base']['quality']

    def get_alternative_font(self):
        return ImageFont.truetype(self._data['base']['alternative_font'], self.get_font_size())

    def get_alternative_bold_font(self):
        return ImageFont.truetype(self._data['base']['alternative_bold_font'], self.get_bold_font_size())

    def get_font(self):
        return ImageFont.truetype(self._data['base']['font'], self.get_font_size())

    def get_bold_font(self):
        return ImageFont.truetype(self._data['base']['bold_font'], self.get_bold_font_size())

    def get_font_size(self):
        font_size = self._data['base']['font_size']
        if font_size == 1:
            return 240
        elif font_size == 2:
            return 250
        elif font_size == 3:
            return 300
        else:
            return 240

    def get_bold_font_size(self):
        font_size = self._data['base']['bold_font_size']
        if font_size == 1:
            return 260
        elif font_size == 2:
            return 290
        elif font_size == 3:
            return 320
        else:
            return 260

    def get_font_padding_level(self):
        bold_font_size = self._data['base']['bold_font_size'] if 1 <= self._data['base']['bold_font_size'] <= 3 else 1
        font_size = self._data['base']['font_size'] if 1 <= self._data['base']['font_size'] <= 3 else 1
        return bold_font_size + font_size

    def save(self):
        with open(self._path, 'w') as f:
            yaml.dump(self._data, f, encoding='utf-8')

    def enable_shadow(self):
        self._data['global']['shadow']['enable'] = True

    def disable_shadow(self):
        self._data['global']['shadow']['enable'] = False

    def has_shadow_enabled(self):
        return self._data['global']['shadow']['enable']

    def has_white_margin_enabled(self):
        return self._data['global']['white_margin']['enable']

    def enable_white_margin(self):
        self._data['global']['white_margin']['enable'] = True

    def disable_white_margin(self):
        self._data['global']['white_margin']['enable'] = False

    def get_white_margin_width(self) -> int:
        white_margin_width = self._data['global']['white_margin']['width']
        if white_margin_width > 30:
            white_margin_width = 30
        if white_margin_width < 0:
            white_margin_width = 0
        self._data['global']['white_margin']['width'] = white_margin_width
        return white_margin_width

    def enable_equivalent_focal_length(self):
        self._data['global']['focal_length']['use_equivalent_focal_length'] = True

    def disable_equivalent_focal_length(self):
        self._data['global']['focal_length']['use_equivalent_focal_length'] = False

    def use_equivalent_focal_length(self):
        return self._data['global']['focal_length']['use_equivalent_focal_length']

    def enable_padding_with_original_ratio(self):
        self._data['global']['padding_with_original_ratio']['enable'] = True

    def disable_padding_with_original_ratio(self):
        self._data['global']['padding_with_original_ratio']['enable'] = False

    def has_padding_with_original_ratio_enabled(self):
        return self._data['global']['padding_with_original_ratio']['enable']

    def set_layout(self, layout):
        self._data['layout']['type'] = layout

    def get_background_color(self) -> str:
        return self._data['layout']['background_color'] if 'background_color' in self._data['layout'] else '#ffffff'

    def enable_logo(self):
        self._data['layout']['logo_enable'] = True

    def disable_logo(self):
        self._data['layout']['logo_enable'] = False

    def has_logo_enabled(self):
        return self._data['layout']['logo_enable']

    def is_logo_left(self):
        if self._data['layout']['logo_position'] == 'left':
            return True

    def set_logo_left(self):
        self._data['layout']['logo_position'] = 'left'

    def set_logo_right(self):
        self._data['layout']['logo_position'] = 'right'

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

    def get_custom_value(self, location):
        if 'value' in self._data['layout']['elements'][location]:
            return self._data['layout']['elements'][location]['value']
        else:
            return ''

    def set_custom(self, location):
        self._data['layout']['elements'][location]['name'] = 'Custom'
        user_input = input('输入自定义字段的值（上次使用的值为：{}）\n'.format(self.get_custom_value(location)))
        self._data['layout']['elements'][location]['value'] = user_input

    def set_element_name(self, location, name):
        if CUSTOM_VALUE == name:
            self.set_custom(location)
        else:
            self._data['layout']['elements'][location]['name'] = name
