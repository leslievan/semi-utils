import string

from PIL import Image, ImageDraw

printable = set(string.printable)

GRAY = '#6B696A'
NORMAL_HEIGHT = 1000


class ImageProcessor(object):
    """
    水印边框
    """

    def __init__(self, font, bold_font):
        self.font = font
        self.bold_font = bold_font

    def text_to_image(self, content, is_bold=False, fill='black'):
        """
        将文字内容转换为图片
        :param content:
        :param is_bold:
        :param fill:
        :return:
        """
        if content == '':
            content = '   '
        font = self.bold_font if is_bold else self.font
        text_width, text_height = font.getsize(content)
        image = Image.new('RGB', (text_width, text_height), color='white')
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), content, fill=fill, font=font)
        return image

    def normal_watermark(self, container, config, is_logo_left=True):
        """
        生成一个默认布局的水印图片
        :param container: 图片对象
        :param config: 水印配置
        :param is_logo_left: logo 位置
        :return: 添加水印后的图片对象
        """
        ratio = .1 if container.ratio >= 1 else .13
        padding_ratio = .618

        watermark = Image.new('RGB', (int(NORMAL_HEIGHT / ratio), NORMAL_HEIGHT), color='white')
        empty_padding = Image.new('RGB', (10, 50), color='white')

        # 填充左边的文字内容
        left_top = self.text_to_image(container.get_attribute_str(config.left_top), is_bold=config.left_top.is_bold)
        left_bottom = self.text_to_image(container.get_attribute_str(config.left_bottom),
                                         is_bold=config.left_bottom.is_bold, fill=GRAY)
        left = concatenate_image([left_top, empty_padding, left_bottom])
        # 填充右边的文字内容
        right_top = self.text_to_image(container.get_attribute_str(config.right_top), is_bold=config.right_top.is_bold)
        right_bottom = self.text_to_image(container.get_attribute_str(config.right_bottom),
                                          is_bold=config.right_bottom.is_bold, fill=GRAY)
        right = concatenate_image([right_top, empty_padding, right_bottom])

        max_height = max(left.height, right.height)
        left = padding_image(left, int(max_height * padding_ratio), 'tb')
        right = padding_image(right, int(max_height * padding_ratio), 't')
        right = padding_image(right, left.height - right.height, 'b')

        logo = container.get_logo()
        if is_logo_left:
            # 如果 logo 在左边
            append_image_by_side(watermark, [logo, left], is_start=logo is None)
            append_image_by_side(watermark, [right], side='right')
        else:
            # 如果 logo 在右边
            if logo is not None:
                # 如果 logo 不为空，等比例缩小 logo
                logo = padding_image(logo, int(padding_ratio * logo.height))
            # 插入一根线条用于分割 logo 和文字
            line = Image.new('RGB', (20, 1000), color=GRAY)
            line = padding_image(line, int(padding_ratio * line.height * .8))
            append_image_by_side(watermark, [left], is_start=True)
            append_image_by_side(watermark, [logo, line, right], side='right')

        watermark = resize_image_with_width(watermark, container.width)
        image = Image.new('RGB', (container.width, container.height + watermark.height), color='white')
        image.paste(container.img)
        image.paste(watermark, (0, container.height))
        return image

    def square_watermark(self, container):
        """
        生成一个1：1布局的水印图片
        :param container: 图片对象
        :return: 填充白边后的图片对象
        """
        return square_image(container.img)

    def watermark_copyright(self, container, config):
        """
        生成一个只有文字的水印图片
        :param container: 图片对象
        :param config: 水印配置
        config.content: 文字的内容
        config.location: 文字的位置（0: 正下方，1: 左下方，2: 右下方，3:正中心）
        :return: 添加水印后的图片对象
        """
        watermark = self.text_to_image(config.content, is_bold=True)
        if config.location == 0 or config.location == 3:
            offset_x = int((container.width - watermark.width) / 2)
        elif config.location == 1:
            offset_x = int(container.width * .05)
        else:
            offset_x = int(container.width * .95 - watermark.width)

        if config.location == 0:
            offset_y = int(container.height * .95 - watermark.height)
        elif config.location == 3:
            offset_y = int((container.height - watermark.height) / 2)
        else:
            offset_y = int(container.height * .05)
        container.img.paste(watermark, (offset_x, offset_y))
        watermark.close()
        return container.img
