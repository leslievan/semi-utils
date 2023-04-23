import sys
from pathlib import Path

from tqdm import tqdm

from entity.image_container import ImageContainer
from entity.image_processor import ProcessorChain
from init import MARGIN_PROCESSOR
from init import SEPARATE_LINE
from init import SHADOW_PROCESSOR
from init import SIMPLE_PROCESSOR
from init import SQUARE_PROCESSOR
from init import WATERMARK_PROCESSOR
from init import config
from init import root_menu
from utils import get_file_list
from utils import insert_exif


def processing():
    """
    状态100：处理图片
    :return:
    """
    global state

    file_list = get_file_list(config.get_input_dir())
    print('当前共有 {} 张图片待处理'.format(len(file_list)))

    processor_chain = ProcessorChain()

    # 如果需要添加阴影，则添加阴影处理器，阴影处理器优先级最高，但是正方形布局不需要阴影
    if config.has_shadow_enabled() and 'square' != config.get_layout_type():
        processor_chain.add(SHADOW_PROCESSOR)

    # 根据布局添加不同的水印处理器
    if 'normal' == config.get_layout_type() or 'normal_with_right_logo' == config.get_layout_type():
        processor_chain.add(WATERMARK_PROCESSOR)
    elif 'square' == config.get_layout_type():
        processor_chain.add(SQUARE_PROCESSOR)
    elif SIMPLE_PROCESSOR.LAYOUT_VALUE == config.get_layout_type():
        processor_chain.add(SIMPLE_PROCESSOR)
    else:
        processor_chain.add(WATERMARK_PROCESSOR)

    # 如果需要添加白边，且不是正方形布局，则添加白边处理器，白边处理器优先级最低
    if config.has_white_margin_enabled() and 'square' != config.get_layout_type():
        processor_chain.add(MARGIN_PROCESSOR)

    for source_path in tqdm(file_list):
        # 打开图片
        container = ImageContainer(source_path)
        # 添加logo
        if config.has_logo_enabled():
            container.set_logo(config.load_logo(container.make))
        else:
            container.set_logo(None)
        # 使用等效焦距
        container.is_use_equivalent_focal_length(config.use_equivalent_focal_length())

        # 处理图片
        processor_chain.process(container)

        # 保存图片
        target_path = Path(config.get_output_dir()).joinpath(source_path.name)

        with container.get_watermark_img() as watermark:
            watermark.save(target_path, quality=config.get_quality())
        container.close()
        insert_exif(container.exif, target_path)
    print('处理完成，文件已输出至 output 文件夹中，请点击任意键退出或直接关闭'.format(len(file_list)))
    input()
    state = -1


state = 0
current_menu = root_menu
root_menu.set_parent(root_menu)

if __name__ == '__main__':
    while True:
        # 0：主菜单，100：处理图片，-1：退出程序，其他：子菜单
        if state == 0:
            # 显示主菜单
            print(SEPARATE_LINE)
            current_menu.display()
            print(SEPARATE_LINE)

            # 处理用户输入
            user_input = input('输入【y 或回车】按照当前设置开始处理图片，输入【数字】修改设置，输入【r】返回上一层菜单，输入【x】退出程序\n')

            # y 或回车，跳转状态 100，开始处理图片
            if user_input == 'y' or user_input == '':
                state = 100
            # x 退出程序
            elif user_input == 'x' or user_input == 'X':
                sys.exit(0)
            # r 返回上一层
            elif user_input == 'r' or user_input == 'R':
                current_menu = current_menu.get_parent()
            # 数字合法则跳转到对应子菜单
            elif user_input.isdigit() and 1 <= int(user_input) <= len(current_menu.components):
                current_menu = current_menu.components[int(user_input) - 1]
                if current_menu.is_leaf():
                    current_menu.run()
                    current_menu = root_menu
            else:
                print('输入错误，请重新输入')
        elif state == 100:
            # 处理数据的代码
            print(SEPARATE_LINE)
            processing()
        elif state == -1:
            # 退出程序
            sys.exit(0)
        # 保存配置
        config.save()
