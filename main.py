import os
from tqdm import tqdm
from config import Layout, input_dir, config, font, bold_font, get_logo, white_margin_enable, white_margin_width, \
    output_dir, quality, logo_enable
from image_container import ImageContainer
from image_processor import ImageProcessor, padding_image
from utils import get_file_list

if __name__ == '__main__':
    file_list = get_file_list(input_dir)
    layout = Layout(config['layout'])

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
