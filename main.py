import os
from tqdm import tqdm
from config import Layout, input_dir, config, font, bold_font, get_logo, white_margin_enable, white_margin_width, \
    output_dir, quality, logo_enable
from image_container import ImageContainer
from image_processor import ImageProcessor, padding_image
from utils import get_file_list

id_to_name = {'Model': '相机机型', 'Make': '相机厂商', 'LensModel': '镜头型号', 'Custom': '自定义字段',
              'Param': '拍摄参数',
              'Date': '拍摄时间', 'None': '无'}

if __name__ == '__main__':
    file_list = get_file_list(input_dir)
    layout = Layout(config['layout'])

    print('当前共有 {} 张图片待处理'.format(len(file_list)))
    print('当前设置：')
    setting_data = [
        ['布局：{}'.format(layout.type), '厂商 logo'.format(logo_enable)],
        ['左上文字：{}'.format(
            id_to_name[layout.left1.name] if layout.left1.name in id_to_name else '参数错误'), '右上文字：{}'.format(
            id_to_name[layout.right1.name] if layout.right1.name in id_to_name else '参数错误')],
        ['左下文字：{}'.format(
            id_to_name[layout.left2.name] if layout.left2.name in id_to_name else '参数错误'), '右下文字：{}'.format(
            id_to_name[layout.right2.name] if layout.right2.name in id_to_name else '参数错误')]
    ]
    # 计算每列的最大宽度
    column_widths = [max(len(str(item)) for item in column) for column in zip(*setting_data)]

    # 打印表格头
    print("+" + "+".join("-" * (width + 2) for width in column_widths) + "+")

    # 打印表格内容
    for row in setting_data:
        print(
            "| " + " | ".join(str(item).ljust(width) for item, width in zip(row, column_widths)) + " |"
        )

    # 打印表格尾
    print("+" + "+".join("-" * (width + 2) for width in column_widths) + "+")
    user_input = input('输入 y 继续，其他键退出：')
    if user_input != 'y' and user_input != 'Y':
        exit(0)

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
            watermark = padding_image(watermark, int(white_margin_width * container.width / 100), 'ulr')

        # 保存图片
        watermark.save(os.path.join(output_dir, file), quality=quality)
        container.close()
        watermark.close()
    print('处理完成，文件已输出至 output 文件夹中，请点击任意键退出或直接关闭'.format(len(file_list)))
    user_input = input()
    exit(0)
