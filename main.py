import os
from tqdm import tqdm
from config import Layout, input_dir, config, font, bold_font, get_logo, white_margin_enable, white_margin_width, \
    output_dir, quality, logo_enable, save_config, load_config
from image_container import ImageContainer
from image_processor import ImageProcessor, padding_image
from utils import get_file_list

id_to_name = {'Model': '相机机型', 'Make': '相机厂商', 'LensModel': '镜头型号', 'Custom': '自定义字段',
              'Param': '拍摄参数',
              'Date': '拍摄时间', 'None': '无'}


def print_current_setting():
    """
    状态1：开始菜单
    :return:
    """
    global state

    s_line = '+' + '-' * 10 + '+' + '-' * 10 + '+'
    print(s_line)
    print(' ' * 8 + '当前设置')
    print(s_line)
    print(' 【1】: 布局：{}'.format(config['layout']['type']))
    print(' 【2】: Logo：{}'.format(config['logo']['enable']))
    print(' 【3】: 左上文字：{}'.format(id_to_name.setdefault(config['layout']['elements']['left_top']['name']), '值错误'))
    print(
        ' 【4】: 左下文字：{}'.format(id_to_name.setdefault(config['layout']['elements']['left_bottom']['name']), '值错误'))
    print(' 【5】: 右上文字：{}'.format(id_to_name.setdefault(config['layout']['elements']['right_top']['name']), '值错误'))
    print(
        ' 【6】: 右下文字：{}'.format(id_to_name.setdefault(config['layout']['elements']['right_bottom']['name']), '值错误'))
    print(s_line)
    user_input = input('输入【y 或回车】按照当前设置开始处理图片，或输入【数字】修改设置：\n')
    if user_input == 'y' or user_input == '':
        state = 100
    elif user_input.isdigit():
        state = int(user_input)


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
        # 打开图片
        container = ImageContainer(os.path.join(input_dir, file))

        # 添加logo
        if logo_enable:
            container.set_logo(get_logo(container.make))
        else:
            container.set_logo(None)

        # 添加水印
        if 'normal_with_right_logo' == layout.type:
            watermark = processor.normal_watermark(container, layout, is_logo_left=False)
        elif 'square' == layout.type:
            watermark = processor.square_watermark(container)
        else:
            watermark = processor.normal_watermark(container, layout)

        # 添加白框
        if white_margin_enable:
            watermark = padding_image(watermark, int(white_margin_width * container.width / 100), 'tlr')

        # 保存图片
        watermark.save(os.path.join(output_dir, file), quality=quality)
        container.close()
        watermark.close()
    print('处理完成，文件已输出至 output 文件夹中，请点击任意键退出或直接关闭'.format(len(file_list)))
    input()
    state = -1


def modify_layout():
    """
    状态2：修改布局
    :return:
    """
    global state

    while True:
        user_input = input(
            '输入【数字】选择布局类型：【1】: normal, 【2】: normal_with_right_logo, 【3】: square，或输入【0】返回主菜单\n')
        if user_input.isdigit():
            if user_input == '0':
                return
            elif user_input == '1':
                config['layout']['type'] = 'normal'
                return
            elif user_input == '2':
                config['layout']['type'] = 'normal_with_right_logo'
                return
            elif user_input == '3':
                config['layout']['type'] = 'square'
                return
            else:
                print('输入错误，请重新输入')
        else:
            print('输入错误，请重新输入')


def modify_logo():
    """
    状态3：修改 logo
    :return:
    """
    global state

    while True:
        user_input = input('输入【数字】选择是否显示 logo：【1】: 显示 logo, 【2】: 不显示 logo，或输入【0】返回主菜单\n')
        if user_input.isdigit():
            if user_input == '0':
                return
            elif user_input == '1':
                config['logo']['enable'] = True
                return
            elif user_input == '2':
                config['logo']['enable'] = False
                return
            else:
                print('输入错误，请重新输入')
        else:
            print('输入错误，请重新输入')


def modify_element(key):
    """
    状态4-7：修改 logo
    :return:
    """
    global state

    while True:
        user_input = input('输入数字选择显示内容：'
                           '【1】：相机型号, 【2】：相机厂商，【3】：镜头型号，【4】：拍摄参数，'
                           '【5】：拍摄日期，【6】：自定义字段，【7】：不显示，'
                           '或输入【0】返回主菜单\n')
        if user_input.isdigit():
            number = int(user_input)
            if number == 0:
                return
            elif number == 1:
                config['layout']['elements'][key]['name'] = 'Model'
                return
            elif number == 2:
                config['layout']['elements'][key]['name'] = 'Make'
                return
            elif number == 3:
                config['layout']['elements'][key]['name'] = 'LensModel'
                return
            elif number == 4:
                config['layout']['elements'][key]['name'] = 'Param'
                return
            elif number == 5:
                config['layout']['elements'][key]['name'] = 'Date'
                return
            elif number == 6:
                config['layout']['elements'][key]['name'] = 'Custom'
                user_input = input('输入自定义字段的值：\n')
                config['layout']['elements'][key]['value'] = user_input
                return
            elif number == 7:
                config['layout']['elements'][key]['name'] = 'None'
                return
            else:
                print('输入错误，请重新输入')
        else:
            print('输入错误，请重新输入')


if __name__ == '__main__':
    state = 0

    while True:
        if state == 0:
            print_current_setting()
        elif state == 100:
            # 处理数据的代码
            load_config()
            processing()
            save_config()
        elif state == 1:
            modify_layout()
            # 修改布局类型的代码
            state = 0
        elif state == 2:
            modify_logo()
            # 修改logo的代码
            state = 0
        elif state == 3:
            modify_element('left_top')
            # 修改左上文字的代码
            state = 0
        elif state == 4:
            modify_element('left_bottom')
            # 修改左下文字的代码
            state = 0
        elif state == 5:
            modify_element('right_top')
            # 修改右上文字的代码
            state = 0
        elif state == 6:
            modify_element('right_bottom')
            # 修改右下文字的代码
            state = 0
        elif state == -1:
            exit(0)
        else:
            print("输入错误，请重新输入")
            state = 0
