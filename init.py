import logging
import os
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
from entity.image_processor import PureWhiteMarginProcessor
from entity.image_processor import ShadowProcessor
from entity.image_processor import SimpleProcessor
from entity.image_processor import SquareProcessor
from entity.image_processor import WatermarkLeftLogoProcessor
from entity.image_processor import WatermarkProcessor
from entity.image_processor import WatermarkRightLogoProcessor
from entity.menu import *
from enums.constant import *
from gen_video import generate_video

# 如果 logs 不存在，创建 logs
Path('./logs').mkdir(parents=True, exist_ok=True)

# 格式化日志输出
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 添加一个 FileHandler 处理器，将 INFO 级别日志写入 ./logs/info.log 文件中
info_handler = logging.FileHandler('./logs/info.log', mode='w')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

# 添加一个 FileHandler 处理器，将 ERROR 级别日志写入 ./logs/error.log 文件中
error_handler = logging.FileHandler('./logs/error.log', mode='w')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# 添加一个 FileHandler 处理器，将 DEBUG 级别日志写入 ./logs/all.log 文件中
debug_handler = logging.FileHandler('./logs/all.log', mode='w')
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)

# 设置日志输出的格式和级别，并将日志输出到指定文件中
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[debug_handler, info_handler, error_handler])

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
PURE_WHITE_MARGIN_PROCESSOR = PureWhiteMarginProcessor(config)

"""
以下是菜单的组织
"""
# 创建主菜单
root_menu = Menu('【Semi-Utils】\n    当前设置')

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
    LayoutItem.from_processor(PURE_WHITE_MARGIN_PROCESSOR),
]
layout_items_dict = {item.value: item for item in LAYOUT_ITEMS}

for item in LAYOUT_ITEMS:
    item_menu = MenuItem(item.name)
    item_menu._value = item.value
    item_menu.set_procedure(config.set_layout, layout=item.value)
    layout_menu.add(item_menu)

# 创建子菜单：logo
logo_menu = SubMenu('logo')
logo_menu.set_value_getter(config, lambda x: x['layout']['logo_enable'])
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
    ElementItem(FILENAME_NAME, FILENAME_VALUE),
    ElementItem(DATE_FILENAME_NAME, DATE_FILENAME_VALUE),
    ElementItem(DATETIME_FILENAME_NAME, DATETIME_FILENAME_VALUE),
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


def help_gen_video():
    # 如果 help.txt 文件存在，说明已经运行过了，直接运行 generate_video
    if not os.path.exists('help.txt'):
        # 生成 help.txt 文件，下次运行时不再提示
        with open('help.txt', 'w') as f:
            f.write('')
        print('以下提示仅在第一次运行时出现，如果需要重新设置，请删除 help.txt 文件后再次运行')
        print('- 该功能用于将 output 中的图片制作成视频，需要ffmpeg支持，默认在 bin 文件夹中附带')
        print('- 如果需要添加背景音乐，请将音乐文件放在 output 文件夹中，命名为 bgm.mp3')
        # 如果输入的不是数字，提示重新输入
        gap_time = input('- 请输入一个数字，指定两张图片切换之间的间隔时间，建议 2s：')
        while not gap_time.isdigit():
            gap_time = input('提示：你输入的不是数字，请重新输入：')
        config.set("video_gap_time", int(gap_time))
        config.save()

    generate_video(config.get_output_dir(), config.get_or_default("video_gap_time", 2))
    # 输入回车继续
    input("按任意键返回主菜单...")


# 创建菜单项：制作视频
make_video_menu = MenuItem('【新功能】制作视频')
make_video_menu.set_procedure(help_gen_video)
root_menu.add(make_video_menu)

default_logo_menu = SubMenu('【新选项】设置默认 logo，机身无法匹配时将使用默认 logo（比如大疆）')
default_logo_menu.set_value_getter(config, lambda x: x.get("logo")["makes"]["default"]["path"])
default_logo_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(default_logo_menu)

for m in config._makes.values():
    item_menu = MenuItem(m['id'])
    item_menu.set_procedure(config.set_default_logo_path, logo_path=m['path'])
    item_menu._value = m['path']
    default_logo_menu.add(item_menu)


# 更多设置
more_setting_menu = SubMenu('更多设置')
more_setting_menu.set_value_getter(config, lambda x: None)
more_setting_menu.set_compare_method(lambda x, y: False)
root_menu.add(more_setting_menu)

# 创建子菜单：白色边框
white_margin_menu = SubMenu('白色边框')
white_margin_menu.set_value_getter(config, lambda x: x['global']['white_margin']['enable'])
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
                                                  lambda x: x['global']['focal_length']['use_equivalent_focal_length'])
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
