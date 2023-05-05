from dataclasses import dataclass
from pathlib import Path

from entity.config import Config
from entity.image_processor import BackgroundBlurProcessor
from entity.image_processor import BackgroundBlurWithWhiteBorderProcessor
from entity.image_processor import CustomWatermarkProcessor
from entity.image_processor import DarkWatermarkLeftLogoProcessor
from entity.image_processor import DarkWatermarkRightLogoProcessor
from entity.image_processor import EmptyProcessor
from entity.image_processor import MarginProcessor
from entity.image_processor import PaddingToOriginalRatioProcessor
from entity.image_processor import ProcessorComponent
from entity.image_processor import ShadowProcessor
from entity.image_processor import SimpleProcessor
from entity.image_processor import SquareProcessor
from entity.image_processor import WatermarkLeftLogoProcessor
from entity.image_processor import WatermarkProcessor
from entity.image_processor import WatermarkRightLogoProcessor
from entity.menu import *
from enums.constant import CAMERA_MAKE_CAMERA_MODEL_NAME
from enums.constant import CAMERA_MAKE_CAMERA_MODEL_VALUE
from enums.constant import CAMERA_MODEL_LENS_MODEL_NAME
from enums.constant import CAMERA_MODEL_LENS_MODEL_VALUE
from enums.constant import CUSTOM_NAME
from enums.constant import CUSTOM_VALUE
from enums.constant import DATETIME_NAME
from enums.constant import DATETIME_VALUE
from enums.constant import DATE_NAME
from enums.constant import DATE_VALUE
from enums.constant import LENS_MAKE_LENS_MODEL_NAME
from enums.constant import LENS_MAKE_LENS_MODEL_VALUE
from enums.constant import LENS_NAME
from enums.constant import LENS_VALUE
from enums.constant import MAKE_NAME
from enums.constant import MAKE_VALUE
from enums.constant import MODEL_NAME
from enums.constant import MODEL_VALUE
from enums.constant import NONE_NAME
from enums.constant import NONE_VALUE
from enums.constant import PARAM_NAME
from enums.constant import PARAM_VALUE
from enums.constant import TOTAL_PIXEL_NAME
from enums.constant import TOTAL_PIXEL_VALUE

import logging

# 如果 logs 不存在，创建 logs
Path('./logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename='./logs/error.log',
    level=logging.ERROR,
    filemode='w',  # 指定打开文件的方式为写入
)

SEPARATE_LINE = '+' + '-' * 15 + '+' + '-' * 15 + '+'


@dataclass
class ElementItem(object):
    name: str
    value: str


@dataclass
class LayoutItem(object):
    name: str
    value: str
    processor: ProcessorComponent

    @staticmethod
    def from_processor(processor: ProcessorComponent):
        return LayoutItem(processor.LAYOUT_NAME, processor.LAYOUT_ID, processor)


# 读取配置
config = Config('config.yaml')

EMPTY_PROCESSOR = EmptyProcessor(config)
WATERMARK_PROCESSOR = WatermarkProcessor(config)
WATERMARK_LEFT_LOGO_PROCESSOR = WatermarkLeftLogoProcessor(config)
WATERMARK_RIGHT_LOGO_PROCESSOR = WatermarkRightLogoProcessor(config)
MARGIN_PROCESSOR = MarginProcessor(config)
SHADOW_PROCESSOR = ShadowProcessor(config)
SQUARE_PROCESSOR = SquareProcessor(config)
SIMPLE_PROCESSOR = SimpleProcessor(config)
PADDING_TO_ORIGINAL_RATIO_PROCESSOR = PaddingToOriginalRatioProcessor(config)
BACKGROUND_BLUR_PROCESSOR = BackgroundBlurProcessor(config)
BACKGROUND_BLUR_WITH_WHITE_BORDER_PROCESSOR = BackgroundBlurWithWhiteBorderProcessor(config)

"""
以下是菜单的组织
"""
# 创建主菜单
root_menu = Menu('    当前设置')

# 创建子菜单：布局
layout_menu = SubMenu('布局')
layout_menu.set_value_getter(config, lambda x: x['layout']['type'])
layout_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(layout_menu)

LAYOUT_ITEMS = [
    LayoutItem.from_processor(WATERMARK_LEFT_LOGO_PROCESSOR),
    LayoutItem.from_processor(WATERMARK_RIGHT_LOGO_PROCESSOR),
    LayoutItem.from_processor(DarkWatermarkLeftLogoProcessor(config)),
    LayoutItem.from_processor(DarkWatermarkRightLogoProcessor(config)),
    LayoutItem.from_processor(CustomWatermarkProcessor(config)),
    LayoutItem.from_processor(SQUARE_PROCESSOR),
    LayoutItem.from_processor(SIMPLE_PROCESSOR),
    LayoutItem.from_processor(BACKGROUND_BLUR_PROCESSOR),
    LayoutItem.from_processor(BACKGROUND_BLUR_WITH_WHITE_BORDER_PROCESSOR),
]
layout_items_dict = {item.value: item for item in LAYOUT_ITEMS}

for item in LAYOUT_ITEMS:
    item_menu = MenuItem(item.name)
    item_menu._value = item.value
    item_menu.set_procedure(config.set_layout, layout=item.value)
    layout_menu.add(item_menu)

# 创建子菜单：logo
logo_menu = SubMenu('logo')
logo_menu.set_value_getter(config, lambda x: x['logo']['enable'])
logo_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(logo_menu)

# 创建菜单项：logo：启用
logo_enable_menu = MenuItem('启用')
logo_enable_menu._value = True
logo_enable_menu.set_procedure(config.enable_logo)
logo_menu.add(logo_enable_menu)

# 创建菜单项：logo：不启用
logo_disable_menu = MenuItem('不启用')
logo_disable_menu._value = False
logo_disable_menu.set_procedure(config.disable_logo)
logo_menu.add(logo_disable_menu)

# 创建子菜单：左上角文字
left_top_menu = SubMenu('左上角')
left_top_menu.set_value_getter(config, lambda x: x['layout']['elements']['left_top']['name'])
left_top_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(left_top_menu)

# 创建子菜单：左下角文字
left_bottom_menu = SubMenu('左下角')
left_bottom_menu.set_value_getter(config, lambda x: x['layout']['elements']['left_bottom']['name'])
left_bottom_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(left_bottom_menu)

# 创建子菜单：右上角文字
right_top_menu = SubMenu('右上角')
right_top_menu.set_value_getter(config, lambda x: x['layout']['elements']['right_top']['name'])
right_top_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(right_top_menu)

# 创建子菜单：右下角文字
right_bottom_menu = SubMenu('右下角')
right_bottom_menu.set_value_getter(config, lambda x: x['layout']['elements']['right_bottom']['name'])
right_bottom_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(right_bottom_menu)

# 左上角、左下角、右上角、右下角可以使用的文字
ITEM_LIST = [
    ElementItem(MODEL_NAME, MODEL_VALUE),
    ElementItem(MAKE_NAME, MAKE_VALUE),
    ElementItem(LENS_NAME, LENS_VALUE),
    ElementItem(PARAM_NAME, PARAM_VALUE),
    ElementItem(DATETIME_NAME, DATETIME_VALUE),
    ElementItem(DATE_NAME, DATE_VALUE),
    ElementItem(CUSTOM_NAME, CUSTOM_VALUE),
    ElementItem(NONE_NAME, NONE_VALUE),
    ElementItem(LENS_MAKE_LENS_MODEL_NAME, LENS_MAKE_LENS_MODEL_VALUE),
    ElementItem(CAMERA_MODEL_LENS_MODEL_NAME, CAMERA_MODEL_LENS_MODEL_VALUE),
    ElementItem(TOTAL_PIXEL_NAME, TOTAL_PIXEL_VALUE),
    ElementItem(CAMERA_MAKE_CAMERA_MODEL_NAME, CAMERA_MAKE_CAMERA_MODEL_VALUE),
]

# 菜单位置与菜单项的映射
LOCATION_MENU_MAP = {'left_top': left_top_menu,
                     'right_top': right_top_menu,
                     'left_bottom': left_bottom_menu,
                     'right_bottom': right_bottom_menu}

# 将这些条目加入菜单
for location, menu in LOCATION_MENU_MAP.items():
    for item in ITEM_LIST:
        menu_item = MenuItem(item.name)
        menu_item.set_procedure(config.set_element_name, location=location, name=item.value)
        menu_item._value = item.value
        menu.add(menu_item)

# 更多设置
more_setting_menu = SubMenu('更多设置')
more_setting_menu.set_value_getter(config, lambda x: None)
more_setting_menu.set_compare_method(lambda x, y: False)
root_menu.add(more_setting_menu)

# 创建子菜单：白色边框
white_margin_menu = SubMenu('白色边框')
white_margin_menu.set_value_getter(config, lambda x: x['layout']['white_margin']['enable'])
white_margin_menu.set_compare_method(lambda x, y: x == y)
more_setting_menu.add(white_margin_menu)

# 创建菜单项：白色边框：启用
white_margin_enable_menu = MenuItem('启用')
white_margin_enable_menu.set_procedure(config.enable_white_margin)
white_margin_enable_menu._value = True
white_margin_menu.add(white_margin_enable_menu)

# 创建菜单项：白色边框：不启用
white_margin_disable_menu = MenuItem('不启用')
white_margin_disable_menu.set_procedure(config.disable_white_margin)
white_margin_disable_menu._value = False
white_margin_menu.add(white_margin_disable_menu)

# 创建子菜单：等效焦距
use_equivalent_focal_length_menu = SubMenu('等效焦距')
use_equivalent_focal_length_menu.set_value_getter(config,
                                                  lambda x: x['param']['focal_length']['use_equivalent_focal_length'])
use_equivalent_focal_length_menu.set_compare_method(lambda x, y: x == y)
more_setting_menu.add(use_equivalent_focal_length_menu)

# 创建菜单项：等效焦距：启用
use_equivalent_focal_length_enable_menu = MenuItem('启用')
use_equivalent_focal_length_enable_menu.set_procedure(config.enable_equivalent_focal_length)
use_equivalent_focal_length_enable_menu._value = True
use_equivalent_focal_length_menu.add(use_equivalent_focal_length_enable_menu)

# 创建菜单项：等效焦距：不启用
use_equivalent_focal_length_disable_menu = MenuItem('不启用')
use_equivalent_focal_length_disable_menu.set_procedure(config.disable_equivalent_focal_length)
use_equivalent_focal_length_disable_menu._value = False
use_equivalent_focal_length_menu.add(use_equivalent_focal_length_disable_menu)

# 创建子菜单：阴影
shadow_menu = SubMenu('阴影')
shadow_menu.set_value_getter(config, lambda x: x['global']['shadow']['enable'])
shadow_menu.set_compare_method(lambda x, y: x == y)
more_setting_menu.add(shadow_menu)

# 创建菜单项：阴影：启用
shadow_enable_menu = MenuItem('启用')
shadow_enable_menu.set_procedure(config.enable_shadow)
shadow_enable_menu._value = True
shadow_menu.add(shadow_enable_menu)

# 创建菜单项：阴影：不启用
shadow_disable_menu = MenuItem('不启用')
shadow_disable_menu.set_procedure(config.disable_shadow)
shadow_disable_menu._value = False
shadow_menu.add(shadow_disable_menu)

# 创建子菜单：按比例填充
padding_with_ratio_menu = SubMenu('按比例填充')
padding_with_ratio_menu.set_value_getter(config, lambda x: x['global']['padding_with_original_ratio']['enable'])
padding_with_ratio_menu.set_compare_method(lambda x, y: x == y)
more_setting_menu.add(padding_with_ratio_menu)

# 创建菜单项：按比例填充：启用
padding_with_ratio_enable_menu = MenuItem('启用')
padding_with_ratio_enable_menu.set_procedure(config.enable_padding_with_original_ratio)
padding_with_ratio_enable_menu._value = True
padding_with_ratio_menu.add(padding_with_ratio_enable_menu)

# 创建菜单项：按比例填充：不启用
padding_with_ratio_disable_menu = MenuItem('不启用')
padding_with_ratio_disable_menu.set_procedure(config.disable_padding_with_original_ratio)
padding_with_ratio_disable_menu._value = False
padding_with_ratio_menu.add(padding_with_ratio_disable_menu)
