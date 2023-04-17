from entity.config import Config
from entity.menu import *

SEPARATE_LINE = '+' + '-' * 15 + '+' + '-' * 15 + '+'
MODEL_NAME = '相机型号'
MODEL_VALUE = 'Model'
MAKE_NAME = '相机厂商'
MAKE_VALUE = 'Make'
LENS_NAME = '镜头型号'
LENS_VALUE = 'LensModel'
PARAM_NAME = '拍摄参数'
PARAM_VALUE = 'Param'
DATE_NAME = '拍摄时间'
DATE_VALUE = 'Date'
CUSTOM_NAME = '自定义'
CUSTOM_VALUE = 'Custom'
NONE_NAME = '无'
NONE_VALUE = 'None'

# 读取配置
config = Config('config.yaml')

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

# 创建菜单项：布局：normal
normal_menu = MenuItem('normal')
normal_menu.value = 'normal'
normal_menu.set_procedure(config.set_normal_layout)
layout_menu.add(normal_menu)

# 创建菜单项：布局：normal_with_right_logo
normal_with_right_logo_menu = MenuItem('normal(Logo 居右)')
normal_with_right_logo_menu.value = 'normal_with_right_logo'
normal_with_right_logo_menu.set_procedure(config.set_normal_with_right_logo_layout)
layout_menu.add(normal_with_right_logo_menu)

# 创建菜单项：布局：square
square_menu = MenuItem('1:1填充')
square_menu.value = 'square'
square_menu.set_procedure(config.set_square_layout)
layout_menu.add(square_menu)

# 创建子菜单：logo
logo_menu = SubMenu('logo')
logo_menu.set_value_getter(config, lambda x: x['logo']['enable'])
logo_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(logo_menu)

# 创建菜单项：logo：显示
logo_enable_menu = MenuItem('显示')
logo_enable_menu.value = True
logo_enable_menu.set_procedure(config.set_logo_enable)
logo_menu.add(logo_enable_menu)

# 创建菜单项：logo：不显示
logo_disable_menu = MenuItem('不显示')
logo_disable_menu.value = False
logo_disable_menu.set_procedure(config.set_logo_disable)
logo_menu.add(logo_disable_menu)

# 创建子菜单：左上角文字
left_top_menu = SubMenu('左上角')
left_top_menu.set_value_getter(config, lambda x: x['layout']['elements']['left_top']['name'])
left_top_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(left_top_menu)

# 创建菜单项：左上角：相机型号
left_top_model_menu = MenuItem(MODEL_NAME)
left_top_model_menu.set_procedure(config.set_left_top_model)
left_top_model_menu.value = MODEL_VALUE
left_top_menu.add(left_top_model_menu)

# 创建菜单项：左上角：相机厂商
left_top_make_menu = MenuItem(MAKE_NAME)
left_top_make_menu.set_procedure(config.set_left_top_make)
left_top_make_menu.value = MAKE_VALUE
left_top_menu.add(left_top_make_menu)

# 创建菜单项：左上角：镜头型号
left_top_lens_menu = MenuItem(LENS_NAME)
left_top_lens_menu.set_procedure(config.set_left_top_lens)
left_top_lens_menu.value = LENS_VALUE
left_top_menu.add(left_top_lens_menu)

# 创建菜单项：左上角：拍摄参数
left_top_param_menu = MenuItem(PARAM_NAME)
left_top_param_menu.set_procedure(config.set_left_top_param)
left_top_param_menu.value = PARAM_VALUE
left_top_menu.add(left_top_param_menu)

# 创建菜单项：左上角：拍摄日期
left_top_date_menu = MenuItem(DATE_NAME)
left_top_date_menu.set_procedure(config.set_left_top_date)
left_top_date_menu.value = DATE_VALUE
left_top_menu.add(left_top_date_menu)

# 创建菜单项：左上角：自定义字段
left_top_custom_menu = MenuItem(CUSTOM_NAME)
left_top_custom_menu.set_procedure(config.set_left_top_custom)
left_top_custom_menu.value = CUSTOM_VALUE
left_top_menu.add(left_top_custom_menu)

# 创建菜单项：左上角：不显示
left_top_none_menu = MenuItem(NONE_NAME)
left_top_none_menu.set_procedure(config.set_left_top_none)
left_top_none_menu.value = NONE_VALUE
left_top_menu.add(left_top_none_menu)

# 创建子菜单：左下角文字
left_bottom_menu = SubMenu('左下角')
left_bottom_menu.set_value_getter(config, lambda x: x['layout']['elements']['left_bottom']['name'])
left_bottom_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(left_bottom_menu)

# 创建菜单项：左下角：相机型号
left_bottom_model_menu = MenuItem(MODEL_NAME)
left_bottom_model_menu.set_procedure(config.set_left_bottom_model)
left_bottom_model_menu.value = MODEL_VALUE
left_bottom_menu.add(left_bottom_model_menu)

# 创建菜单项：左下角：相机厂商
left_bottom_make_menu = MenuItem(MAKE_NAME)
left_bottom_make_menu.set_procedure(config.set_left_bottom_make)
left_bottom_make_menu.value = MAKE_VALUE
left_bottom_menu.add(left_bottom_make_menu)

# 创建菜单项：左下角：镜头型号
left_bottom_lens_menu = MenuItem(LENS_NAME)
left_bottom_lens_menu.set_procedure(config.set_left_bottom_lens)
left_bottom_lens_menu.value = LENS_VALUE
left_bottom_menu.add(left_bottom_lens_menu)

# 创建菜单项：左下角：拍摄参数
left_bottom_param_menu = MenuItem(PARAM_NAME)
left_bottom_param_menu.set_procedure(config.set_left_bottom_param)
left_bottom_param_menu.value = PARAM_VALUE
left_bottom_menu.add(left_bottom_param_menu)

# 创建菜单项：左下角：拍摄日期
left_bottom_date_menu = MenuItem(DATE_NAME)
left_bottom_date_menu.set_procedure(config.set_left_bottom_date)
left_bottom_date_menu.value = DATE_VALUE
left_bottom_menu.add(left_bottom_date_menu)

# 创建菜单项：左下角：自定义字段
left_bottom_custom_menu = MenuItem(CUSTOM_NAME)
left_bottom_custom_menu.set_procedure(config.set_left_bottom_custom)
left_bottom_custom_menu.value = CUSTOM_VALUE
left_bottom_menu.add(left_bottom_custom_menu)

# 创建菜单项：左下角：不显示
left_bottom_none_menu = MenuItem(NONE_NAME)
left_bottom_none_menu.set_procedure(config.set_left_bottom_none)
left_bottom_none_menu.value = NONE_VALUE
left_bottom_menu.add(left_bottom_none_menu)

# 创建子菜单：右上角文字
right_top_menu = SubMenu('右上角')
right_top_menu.set_value_getter(config, lambda x: x['layout']['elements']['right_top']['name'])
right_top_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(right_top_menu)

# 创建菜单项：右上角：相机型号
right_top_model_menu = MenuItem(MODEL_NAME)
right_top_model_menu.set_procedure(config.set_right_top_model)
right_top_model_menu.value = MODEL_VALUE
right_top_menu.add(right_top_model_menu)

# 创建菜单项：右上角：相机厂商
right_top_make_menu = MenuItem(MAKE_NAME)
right_top_make_menu.set_procedure(config.set_right_top_make)
right_top_make_menu.value = MAKE_VALUE
right_top_menu.add(right_top_make_menu)

# 创建菜单项：右上角：镜头型号
right_top_lens_menu = MenuItem(LENS_NAME)
right_top_lens_menu.set_procedure(config.set_right_top_lens)
right_top_lens_menu.value = LENS_VALUE
right_top_menu.add(right_top_lens_menu)

# 创建菜单项：右上角：拍摄参数
right_top_param_menu = MenuItem(PARAM_NAME)
right_top_param_menu.set_procedure(config.set_right_top_param)
right_top_param_menu.value = PARAM_VALUE
right_top_menu.add(right_top_param_menu)

# 创建菜单项：右上角：拍摄日期
right_top_date_menu = MenuItem(DATE_NAME)
right_top_date_menu.set_procedure(config.set_right_top_date)
right_top_date_menu.value = DATE_VALUE
right_top_menu.add(right_top_date_menu)

# 创建菜单项：右上角：自定义字段
right_top_custom_menu = MenuItem(CUSTOM_NAME)
right_top_custom_menu.set_procedure(config.set_right_top_custom)
right_top_custom_menu.value = CUSTOM_VALUE
right_top_menu.add(right_top_custom_menu)

# 创建菜单项：右上角：不显示
right_top_none_menu = MenuItem(NONE_NAME)
right_top_none_menu.set_procedure(config.set_right_top_none)
right_top_none_menu.value = NONE_VALUE
right_top_menu.add(right_top_none_menu)

# 创建子菜单：右下角文字
right_bottom_menu = SubMenu('右下角')
right_bottom_menu.set_value_getter(config, lambda x: x['layout']['elements']['right_bottom']['name'])
right_bottom_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(right_bottom_menu)

# 创建菜单项：右下角：相机型号
right_bottom_model_menu = MenuItem(MODEL_NAME)
right_bottom_model_menu.set_procedure(config.set_right_bottom_model)
right_bottom_model_menu.value = MODEL_VALUE
right_bottom_menu.add(right_bottom_model_menu)

# 创建菜单项：右下角：相机厂商
right_bottom_make_menu = MenuItem(MAKE_NAME)
right_bottom_make_menu.set_procedure(config.set_right_bottom_make)
right_bottom_make_menu.value = MAKE_VALUE
right_bottom_menu.add(right_bottom_make_menu)

# 创建菜单项：右下角：镜头型号
right_bottom_lens_menu = MenuItem(LENS_NAME)
right_bottom_lens_menu.set_procedure(config.set_right_bottom_lens)
right_bottom_lens_menu.value = LENS_VALUE
right_bottom_menu.add(right_bottom_lens_menu)

# 创建菜单项：右下角：拍摄参数
right_bottom_param_menu = MenuItem(PARAM_NAME)
right_bottom_param_menu.set_procedure(config.set_right_bottom_param)
right_bottom_param_menu.value = PARAM_VALUE
right_bottom_menu.add(right_bottom_param_menu)

# 创建菜单项：右下角：拍摄日期
right_bottom_date_menu = MenuItem(DATE_NAME)
right_bottom_date_menu.set_procedure(config.set_right_bottom_date)
right_bottom_date_menu.value = DATE_VALUE
right_bottom_menu.add(right_bottom_date_menu)

# 创建菜单项：右下角：自定义字段
right_bottom_custom_menu = MenuItem(CUSTOM_NAME)
right_bottom_custom_menu.set_procedure(config.set_right_bottom_custom)
right_bottom_custom_menu.value = CUSTOM_VALUE
right_bottom_menu.add(right_bottom_custom_menu)

# 创建菜单项：右下角：不显示
right_bottom_none_menu = MenuItem(NONE_NAME)
right_bottom_none_menu.set_procedure(config.set_right_bottom_none)
right_bottom_none_menu.value = NONE_VALUE
right_bottom_menu.add(right_bottom_none_menu)

# 创建子菜单：白色边框
white_margin_menu = SubMenu('白色边框')
white_margin_menu.set_value_getter(config, lambda x: x['layout']['white_margin']['enable'])
white_margin_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(white_margin_menu)

# 创建菜单项：白色边框：显示
white_margin_enable_menu = MenuItem('显示')
white_margin_enable_menu.set_procedure(config.set_white_margin_enable)
white_margin_enable_menu.value = True
white_margin_menu.add(white_margin_enable_menu)

# 创建菜单项：白色边框：不显示
white_margin_disable_menu = MenuItem('不显示')
white_margin_disable_menu.set_procedure(config.set_white_margin_disable)
white_margin_disable_menu.value = False
white_margin_menu.add(white_margin_disable_menu)

# 创建子菜单：等效焦距
use_equivalent_focal_length_menu = SubMenu('等效焦距')
use_equivalent_focal_length_menu.set_value_getter(config,
                                                  lambda x: x['param']['focal_length']['use_equivalent_focal_length'])
use_equivalent_focal_length_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(use_equivalent_focal_length_menu)

# 创建菜单项：等效焦距：使用
use_equivalent_focal_length_enable_menu = MenuItem('使用')
use_equivalent_focal_length_enable_menu.set_procedure(config.set_use_equivalent_focal_length_enable)
use_equivalent_focal_length_enable_menu.value = True
use_equivalent_focal_length_menu.add(use_equivalent_focal_length_enable_menu)

# 创建菜单项：等效焦距：不使用
use_equivalent_focal_length_disable_menu = MenuItem('不使用')
use_equivalent_focal_length_disable_menu.set_procedure(config.set_use_equivalent_focal_length_disable)
use_equivalent_focal_length_disable_menu.value = False
use_equivalent_focal_length_menu.add(use_equivalent_focal_length_disable_menu)
