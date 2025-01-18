import logging
import sys
from multiprocessing.pool import Pool
from pathlib import Path

from tqdm import tqdm
import os
from entity.image_container import ImageContainer
from entity.image_processor import ProcessorChain
from enums.constant import DEBUG
from init import MARGIN_PROCESSOR
from init import PADDING_TO_ORIGINAL_RATIO_PROCESSOR
from init import SEPARATE_LINE
from init import SHADOW_PROCESSOR
from init import SIMPLE_PROCESSOR
from init import config
from init import layout_items_dict
from init import root_menu
from utils import ENCODING
from utils import get_file_list


def get_new_filename(original_path):
    from datetime import datetime
    # 检查文件路径是否存在
    if os.path.exists(original_path):
        # 拆分文件名和扩展名
        file_dir, file_name = os.path.split(original_path)
        file_root, file_ext = os.path.splitext(file_name)

        # 生成新的文件名
        new_file_name = f"{file_root}{datetime.now().strftime('%m%d-%H%M')}{file_ext}"
        new_file_path = os.path.join(file_dir, new_file_name)
        return new_file_path
    else:
        return original_path


def image_process_callback(processor_chain_, source_path_):
    # 打开图片
    container = ImageContainer(source_path_)

    # 使用等效焦距
    container.is_use_equivalent_focal_length(config.use_equivalent_focal_length())

    # 处理图片
    try:
        processor_chain_.process(container)
    except Exception as e:
        logging.exception(f'Error: {str(e)}')
        if DEBUG:
            raise e
        else:
            print(f'\nError: 文件：{source_path_} 处理失败，请检查日志')

    # 保存图片
    if config.get_output_dir():
        # 使用output文件夹
        target_path = Path(config.get_output_dir(), encoding=ENCODING).joinpath(source_path_.name)
    else:
        # 保存在原来的文件夹中
        target_path = get_new_filename(Path(config.get_input_dir(), encoding=ENCODING).joinpath(source_path_.name))

    container.save(target_path, quality=config.get_quality())
    container.close()


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
    if config.get_layout_type() in layout_items_dict:
        processor_chain.add(layout_items_dict.get(config.get_layout_type()).processor)
    else:
        processor_chain.add(SIMPLE_PROCESSOR)

    # 如果需要添加白边，且是水印布局，则添加白边处理器，白边处理器优先级最低
    if config.has_white_margin_enabled() and 'watermark' in config.get_layout_type():
        processor_chain.add(MARGIN_PROCESSOR)

    # 如果需要按原有比例填充，且不是正方形布局，则添加填充处理器
    if config.has_padding_with_original_ratio_enabled() and 'square' != config.get_layout_type():
        processor_chain.add(PADDING_TO_ORIGINAL_RATIO_PROCESSOR)

    def update(*a):
        # 这个函数将会在每个进程完成后被调用，用来更新进度条
        pbar.update()

    # 初始化tqdm进度条
    pbar = tqdm(total=len(file_list))

    # 限制最大并发进程数
    pool = Pool(5)

    # 对于file_list中的每个source_path，异步地启动进程
    for source_path in file_list:
        pool.apply_async(image_process_callback, args=(processor_chain, source_path), callback=update)

    # 关闭进程池，不再接受新的任务
    pool.close()

    # 等待所有进程完成
    pool.join()

    # 完成所有任务后，关闭tqdm进度条
    pbar.close()

    path = config.get_output_dir()
    option = input(f'处理完成，文件已输出至 {path if path else "input"} 文件夹中，输入【r】返回主菜单，输入【x】退出程序\n')
    if DEBUG:
        sys.exit(0)
    else:
        if option == 'x' or option == 'X':
            state = -1
            # r 返回上一层
        else:
            state = 0


state = 0
current_menu = root_menu
root_menu.set_parent(root_menu)

if __name__ == '__main__':
    print(SEPARATE_LINE)
    print('''
本工具为开源工具，遵循 Apache 2.0 License 发布。如果您在使用过程中遇到问题，请联系作者：
GitHub: @leslievan
Bilibili: @吨吨吨的半夏
项目介绍：https://www.bilibili.com/video/BV11A411U7Kn
项目地址：https://github.com/leslievan/semi-utils
项目介绍（博客）：https://lsvm.xyz/2023/02/semi-utils-intro/
项目发布页：https://docs.qq.com/sheet/DTXF5c2lHeUZYREtw
''')
    while True:
        try:
            # 0：主菜单，100：处理图片，-1：退出程序，其他：子菜单
            if state == 0:
                # 显示主菜单
                print(SEPARATE_LINE)
                current_menu.display()
                print(SEPARATE_LINE)

                # 处理用户输入
                user_input = input(
                    '输入【y 或回车】按照当前设置开始处理图片，输入【数字】修改设置，输入【r】返回上一层菜单，输入【x】退出程序\n')

                # y 或回车，跳转状态 100，开始处理图片
                if user_input == 'y' or user_input == '':
                    state = 100
                # x 退出程序
                elif user_input.upper() == 'X':
                    sys.exit(0)
                # r 返回上一层
                elif user_input.upper() == 'R':
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
            elif state == -2:
                sys.exit(1)
            # 保存配置
            config.save()
        except Exception as e:
            logging.exception(f'Error: {str(e)}')
            if DEBUG:
                raise e
