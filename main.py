import sys

from tqdm import tqdm

from config import *
from image_container import ImageContainer
from image_processor import ImageProcessor
from image_processor import padding_image
from menu import *
from utils import copy_exif_data
from utils import get_file_list

s_line = '+' + '-' * 15 + '+' + '-' * 15 + '+'

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


def processing():
    """
    状态1：处理图片
    :return:
    """
    global state

    file_list = get_file_list(input_dir)
    layout = Layout(config['layout'])
    print('当前共有 {} 张图片待处理'.format(len(file_list)))
    processor = ImageProcessor(font, bold_font)
    for file in tqdm(file_list):
        source_path = os.path.join(input_dir, file)
        # 打开图片
        container = ImageContainer(source_path)

        # 添加logo
        if logo_enable:
            container.set_logo(get_logo(container.make))
        else:
            container.set_logo(None)

        # 使用等效焦距
        container.is_use_equivalent_focal_length(config['param']['focal_length']['use_equivalent_focal_length'])

        # 添加水印
        if 'normal_with_right_logo' == layout.type:
            watermark = processor.normal_watermark(container, layout, is_logo_left=False)
        elif 'square' == layout.type:
            watermark = processor.square_watermark(container)
        else:
            watermark = processor.normal_watermark(container, layout)

        # 添加白框
        if config['layout']['white_margin']['enable']:
            watermark = padding_image(watermark, int(white_margin_width * min(container.width, container.height) / 100),
                                      'tlr')

        # 保存图片
        target_path = os.path.join(output_dir, file)
        watermark.save(target_path, quality=quality)
        container.close()
        watermark.close()
        copy_exif_data(source_path, target_path)
    print('处理完成，文件已输出至 output 文件夹中，请点击任意键退出或直接关闭'.format(len(file_list)))
    input()
    state = -1


state = 0

# 创建主菜单
root_menu = Menu('    当前设置')

# 创建子菜单：布局
layout_menu = SubMenu('布局')
layout_menu.set_value(config, lambda x: x['layout']['type'])
layout_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(layout_menu)

# 创建菜单项：布局：normal
normal_menu = MenuItem('normal')
normal_menu.value = normal_menu.name
normal_menu.set_process(set_normal_layout)
layout_menu.add(normal_menu)

# 创建菜单项：布局：normal_with_right_logo
normal_with_right_logo_menu = MenuItem('normal_with_right_logo')
normal_with_right_logo_menu.value = normal_with_right_logo_menu.name
normal_with_right_logo_menu.set_process(set_normal_with_right_logo_layout)
layout_menu.add(normal_with_right_logo_menu)

# 创建菜单项：布局：square
square_menu = MenuItem('square')
square_menu.value = square_menu.name
square_menu.set_process(set_square_layout)
layout_menu.add(square_menu)

# 创建子菜单：logo
logo_menu = SubMenu('logo')
logo_menu.set_value(config, lambda x: x['logo']['enable'])
logo_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(logo_menu)

# 创建菜单项：logo：显示
logo_enable_menu = MenuItem('显示')
logo_enable_menu.value = True
logo_enable_menu.set_process(set_logo_enable)
logo_menu.add(logo_enable_menu)

# 创建菜单项：logo：不显示
logo_disable_menu = MenuItem('不显示')
logo_disable_menu.value = False
logo_disable_menu.set_process(set_logo_disable)
logo_menu.add(logo_disable_menu)

# 创建子菜单：左上角文字
left_top_menu = SubMenu('左上角')
left_top_menu.set_value(config, lambda x: x['layout']['elements']['left_top']['name'])
left_top_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(left_top_menu)

# 创建菜单项：左上角：相机型号
left_top_model_menu = MenuItem(MODEL_NAME)
left_top_model_menu.set_process(set_left_top_model)
left_top_model_menu.value = MODEL_VALUE
left_top_menu.add(left_top_model_menu)

# 创建菜单项：左上角：相机厂商
left_top_make_menu = MenuItem(MAKE_NAME)
left_top_make_menu.set_process(set_left_top_make)
left_top_make_menu.value = MAKE_VALUE
left_top_menu.add(left_top_make_menu)

# 创建菜单项：左上角：相机镜头
left_top_lens_menu = MenuItem(LENS_NAME)
left_top_lens_menu.set_process(set_left_top_lens)
left_top_lens_menu.value = LENS_VALUE
left_top_menu.add(left_top_lens_menu)

# 创建菜单项：左上角：拍摄参数
left_top_param_menu = MenuItem(PARAM_NAME)
left_top_param_menu.set_process(set_left_top_param)
left_top_param_menu.value = PARAM_VALUE
left_top_menu.add(left_top_param_menu)

# 创建菜单项：左上角：拍摄日期
left_top_date_menu = MenuItem(DATE_NAME)
left_top_date_menu.set_process(set_left_top_date)
left_top_date_menu.value = DATE_VALUE
left_top_menu.add(left_top_date_menu)

# 创建菜单项：左上角：自定义字段
left_top_custom_menu = MenuItem(CUSTOM_NAME)
left_top_custom_menu.set_process(set_left_top_custom)
left_top_custom_menu.value = CUSTOM_VALUE
left_top_menu.add(left_top_custom_menu)

# 创建菜单项：左上角：不显示
left_top_none_menu = MenuItem(NONE_NAME)
left_top_none_menu.set_process(set_left_top_none)
left_top_none_menu.value = NONE_VALUE
left_top_menu.add(left_top_none_menu)

# 创建子菜单：左下角文字
left_bottom_menu = SubMenu('左下角')
left_bottom_menu.set_value(config, lambda x: x['layout']['elements']['left_bottom']['name'])
left_bottom_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(left_bottom_menu)

# 创建菜单项：左下角：相机型号
left_bottom_model_menu = MenuItem(MODEL_NAME)
left_bottom_model_menu.set_process(set_left_bottom_model)
left_bottom_model_menu.value = MODEL_VALUE
left_bottom_menu.add(left_bottom_model_menu)

# 创建菜单项：左下角：相机厂商
left_bottom_make_menu = MenuItem(MAKE_NAME)
left_bottom_make_menu.set_process(set_left_bottom_make)
left_bottom_make_menu.value = MAKE_VALUE
left_bottom_menu.add(left_bottom_make_menu)

# 创建菜单项：左下角：相机镜头
left_bottom_lens_menu = MenuItem(LENS_NAME)
left_bottom_lens_menu.set_process(set_left_bottom_lens)
left_bottom_lens_menu.value = LENS_VALUE
left_bottom_menu.add(left_bottom_lens_menu)

# 创建菜单项：左下角：拍摄参数
left_bottom_param_menu = MenuItem(PARAM_NAME)
left_bottom_param_menu.set_process(set_left_bottom_param)
left_bottom_param_menu.value = PARAM_VALUE
left_bottom_menu.add(left_bottom_param_menu)

# 创建菜单项：左下角：拍摄日期
left_bottom_date_menu = MenuItem(DATE_NAME)
left_bottom_date_menu.set_process(set_left_bottom_date)
left_bottom_date_menu.value = DATE_VALUE
left_bottom_menu.add(left_bottom_date_menu)

# 创建菜单项：左下角：自定义字段
left_bottom_custom_menu = MenuItem(CUSTOM_NAME)
left_bottom_custom_menu.set_process(set_left_bottom_custom)
left_bottom_custom_menu.value = CUSTOM_VALUE
left_bottom_menu.add(left_bottom_custom_menu)

# 创建菜单项：左下角：不显示
left_bottom_none_menu = MenuItem(NONE_NAME)
left_bottom_none_menu.set_process(set_left_bottom_none)
left_bottom_none_menu.value = NONE_VALUE
left_bottom_menu.add(left_bottom_none_menu)

# 创建子菜单：右上角文字
right_top_menu = SubMenu('右上角')
right_top_menu.set_value(config, lambda x: x['layout']['elements']['right_top']['name'])
right_top_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(right_top_menu)

# 创建菜单项：右上角：相机型号
right_top_model_menu = MenuItem(MODEL_NAME)
right_top_model_menu.set_process(set_right_top_model)
right_top_model_menu.value = MODEL_VALUE
right_top_menu.add(right_top_model_menu)

# 创建菜单项：右上角：相机厂商
right_top_make_menu = MenuItem(MAKE_NAME)
right_top_make_menu.set_process(set_right_top_make)
right_top_make_menu.value = MAKE_VALUE
right_top_menu.add(right_top_make_menu)

# 创建菜单项：右上角：相机镜头
right_top_lens_menu = MenuItem(LENS_NAME)
right_top_lens_menu.set_process(set_right_top_lens)
right_top_lens_menu.value = LENS_VALUE
right_top_menu.add(right_top_lens_menu)

# 创建菜单项：右上角：拍摄参数
right_top_param_menu = MenuItem(PARAM_NAME)
right_top_param_menu.set_process(set_right_top_param)
right_top_param_menu.value = PARAM_VALUE
right_top_menu.add(right_top_param_menu)

# 创建菜单项：右上角：拍摄日期
right_top_date_menu = MenuItem(DATE_NAME)
right_top_date_menu.set_process(set_right_top_date)
right_top_date_menu.value = DATE_VALUE
right_top_menu.add(right_top_date_menu)

# 创建菜单项：右上角：自定义字段
right_top_custom_menu = MenuItem(CUSTOM_NAME)
right_top_custom_menu.set_process(set_right_top_custom)
right_top_custom_menu.value = CUSTOM_VALUE
right_top_menu.add(right_top_custom_menu)

# 创建菜单项：右上角：不显示
right_top_none_menu = MenuItem(NONE_NAME)
right_top_none_menu.set_process(set_right_top_none)
right_top_none_menu.value = NONE_VALUE
right_top_menu.add(right_top_none_menu)

# 创建子菜单：右下角文字
right_bottom_menu = SubMenu('右下角')
right_bottom_menu.set_value(config, lambda x: x['layout']['elements']['right_bottom']['name'])
right_bottom_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(right_bottom_menu)

# 创建菜单项：右下角：相机型号
right_bottom_model_menu = MenuItem(MODEL_NAME)
right_bottom_model_menu.set_process(set_right_bottom_model)
right_bottom_model_menu.value = MODEL_VALUE
right_bottom_menu.add(right_bottom_model_menu)

# 创建菜单项：右下角：相机厂商
right_bottom_make_menu = MenuItem(MAKE_NAME)
right_bottom_make_menu.set_process(set_right_bottom_make)
right_bottom_make_menu.value = MAKE_VALUE
right_bottom_menu.add(right_bottom_make_menu)

# 创建菜单项：右下角：相机镜头
right_bottom_lens_menu = MenuItem(LENS_NAME)
right_bottom_lens_menu.set_process(set_right_bottom_lens)
right_bottom_lens_menu.value = LENS_VALUE
right_bottom_menu.add(right_bottom_lens_menu)

# 创建菜单项：右下角：拍摄参数
right_bottom_param_menu = MenuItem(PARAM_NAME)
right_bottom_param_menu.set_process(set_right_bottom_param)
right_bottom_param_menu.value = PARAM_VALUE
right_bottom_menu.add(right_bottom_param_menu)

# 创建菜单项：右下角：拍摄日期
right_bottom_date_menu = MenuItem(DATE_NAME)
right_bottom_date_menu.set_process(set_right_bottom_date)
right_bottom_date_menu.value = DATE_VALUE
right_bottom_menu.add(right_bottom_date_menu)

# 创建菜单项：右下角：自定义字段
right_bottom_custom_menu = MenuItem(CUSTOM_NAME)
right_bottom_custom_menu.set_process(set_right_bottom_custom)
right_bottom_custom_menu.value = CUSTOM_VALUE
right_bottom_menu.add(right_bottom_custom_menu)

# 创建菜单项：右下角：不显示
right_bottom_none_menu = MenuItem(NONE_NAME)
right_bottom_none_menu.set_process(set_right_bottom_none)
right_bottom_none_menu.value = NONE_VALUE
right_bottom_menu.add(right_bottom_none_menu)

# 创建子菜单：白色边框
white_margin_menu = SubMenu('白色边框')
white_margin_menu.set_value(config, lambda x: x['layout']['white_margin']['enable'])
white_margin_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(white_margin_menu)

# 创建菜单项：白色边框：显示
white_margin_enable_menu = MenuItem('显示')
white_margin_enable_menu.set_process(set_white_margin_enable())
white_margin_enable_menu.value = True
white_margin_menu.add(white_margin_enable_menu)

# 创建菜单项：白色边框：不显示
white_margin_disable_menu = MenuItem('不显示')
white_margin_disable_menu.set_process(set_white_margin_disable())
white_margin_disable_menu.value = False
white_margin_menu.add(white_margin_disable_menu)

# 创建子菜单：等效焦距
use_equivalent_focal_length_menu = SubMenu('等效焦距')
use_equivalent_focal_length_menu.set_value(config, lambda x: x['param']['focal_length']['use_equivalent_focal_length'])
use_equivalent_focal_length_menu.set_compare_method(lambda x, y: x == y)
root_menu.add(use_equivalent_focal_length_menu)

# 创建菜单项：等效焦距：使用
use_equivalent_focal_length_enable_menu = MenuItem('使用')
use_equivalent_focal_length_enable_menu.set_process(set_use_equivalent_focal_length_enable())
use_equivalent_focal_length_enable_menu.value = True
use_equivalent_focal_length_menu.add(use_equivalent_focal_length_enable_menu)

# 创建菜单项：等效焦距：不使用
use_equivalent_focal_length_disable_menu = MenuItem('不使用')
use_equivalent_focal_length_disable_menu.set_process(set_use_equivalent_focal_length_disable())
use_equivalent_focal_length_disable_menu.value = False
use_equivalent_focal_length_menu.add(use_equivalent_focal_length_disable_menu)

if __name__ == '__main__':
    while True:
        # 0：主菜单，100：处理数据，其他：子菜单
        if state == 0:
            root_menu.display()
            print(s_line)
            user_input = input('输入【y 或回车】按照当前设置开始处理图片，输入【数字】修改设置，输入【x】退出程序\n')
            if user_input == 'y' or user_input == '':
                state = 100
            elif user_input == 'x' or user_input == 'X':
                sys.exit(0)
            elif user_input.isdigit() and 1 <= int(user_input) <= len(root_menu.components):
                state = int(user_input)
            else:
                print('输入错误，请重新输入')
        elif state == 100:
            # 处理数据的代码
            print(s_line)
            load_config()
            processing()
        else:
            print(s_line)
            submenu = root_menu.components[state - 1]
            submenu.display()
            user_input = input('输入【数字】修改设置，输入【x】退出程序\n')
            if user_input == 'x' or user_input == 'X':
                sys.exit(0)
            elif user_input.isdigit() and 1 <= int(user_input) <= len(submenu.components):
                submenu.components[int(user_input) - 1].process()
                state = 0
            else:
                print('输入错误，请重新输入')
        save_config()
