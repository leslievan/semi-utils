import string

from PIL import Image
from PIL import ImageFilter
from PIL import ImageOps

from entity.config import Config
from entity.image_container import ImageContainer
from utils import append_image_by_side
from utils import concatenate_image
from utils import merge_images
from utils import padding_image
from utils import resize_image_with_height
from utils import resize_image_with_width
from utils import square_image
from utils import text_to_image

printable = set(string.printable)

GRAY = '#CBCBC9'
NORMAL_HEIGHT = 1000
SMALL_HORIZONTAL_GAP = Image.new('RGB', (50, 20), color='white')
MIDDLE_HORIZONTAL_GAP = Image.new('RGB', (100, 20), color='white')
LARGE_HORIZONTAL_GAP = Image.new('RGB', (200, 20), color='white')
SMALL_VERTICAL_GAP = Image.new('RGB', (20, 50), color='white')
MIDDLE_VERTICAL_GAP = Image.new('RGB', (20, 100), color='white')
LARGE_VERTICAL_GAP = Image.new('RGB', (20, 200), color='white')


class ProcessorComponent:
    """
    图片处理器组件
    """
    LAYOUT_ID = None

    def process(self, container: ImageContainer) -> None:
        """
        处理图片容器中的 watermark_img，将处理后的图片放回容器中
        """
        raise NotImplementedError

    def add(self, component):
        raise NotImplementedError


class ProcessorChain(ProcessorComponent):
    def __init__(self):
        self.components = []

    def add(self, component) -> None:
        self.components.append(component)

    def process(self, container: ImageContainer) -> None:
        for component in self.components:
            component.process(container)


class EmptyProcessor(ProcessorComponent):
    LAYOUT_ID = 'empty'

    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        pass


class ShadowProcessor(ProcessorComponent):
    LAYOUT_ID = 'shadow'

    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        # 加载图像
        image = container.get_watermark_img()

        max_pixel = max(image.width, image.height)
        # 计算阴影边框大小
        radius = int(max_pixel / 512)

        # 创建阴影效果
        shadow = Image.new('RGB', image.size, color='#6B696A')
        shadow = ImageOps.expand(shadow, border=(radius * 2, radius * 2, radius * 2, radius * 2), fill=(255, 255, 255))
        # 模糊阴影
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=radius))

        # 将原始图像放置在阴影图像上方
        shadow.paste(image, (radius, radius))
        container.update_watermark_img(shadow)


class SquareProcessor(ProcessorComponent):
    LAYOUT_ID = 'square'

    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        image = container.get_watermark_img()
        container.update_watermark_img(square_image(image, auto_close=False))


class WatermarkProcessor(ProcessorComponent):
    LAYOUT_ID = 'watermark'

    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        """
        生成一个默认布局的水印图片
        :param container: 图片对象
        :return: 添加水印后的图片对象
        """
        config = self.config

        ratio = (.04 if container.get_ratio() >= 1 else .09) + 0.02 * config.get_font_padding_level()
        padding_ratio = (.52 if container.get_ratio() >= 1 else .7) - 0.04 * config.get_font_padding_level()

        # 创建一个空白的水印图片
        watermark = Image.new('RGB', (int(NORMAL_HEIGHT / ratio), NORMAL_HEIGHT), color='white')

        with Image.new('RGB', (10, 100), color='white') as empty_padding:
            # 填充左边的文字内容
            left_top = text_to_image(container.get_attribute_str(config.get_left_top()),
                                     config.get_font(),
                                     config.get_bold_font(),
                                     is_bold=config.get_left_top().is_bold())
            left_bottom = text_to_image(container.get_attribute_str(config.get_left_bottom()),
                                        config.get_font(),
                                        config.get_bold_font(),
                                        is_bold=config.get_left_bottom().is_bold(), fill=GRAY)
            left = concatenate_image([left_top, empty_padding, left_bottom])
            # 填充右边的文字内容
            right_top = text_to_image(container.get_attribute_str(config.get_right_top()),
                                      config.get_font(),
                                      config.get_bold_font(),
                                      is_bold=config.get_right_top().is_bold())
            right_bottom = text_to_image(container.get_attribute_str(config.get_right_bottom()),
                                         config.get_font(),
                                         config.get_bold_font(),
                                         is_bold=config.get_right_bottom().is_bold(), fill=GRAY)
            right = concatenate_image([right_top, empty_padding, right_bottom])

        max_height = max(left.height, right.height)
        left = padding_image(left, int(max_height * padding_ratio), 'tb')
        right = padding_image(right, int(max_height * padding_ratio), 't')
        right = padding_image(right, left.height - right.height, 'b')

        logo = container.get_logo()
        if config.is_logo_left():
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
            line.close()
        left.close()
        right.close()

        watermark = resize_image_with_width(watermark, container.get_width())
        image = Image.new('RGB', (container.get_width(), container.get_height() + watermark.height), color='white')
        image.paste(container.get_watermark_img())
        image.paste(watermark, (0, container.get_height()))
        container.update_watermark_img(image)


class MarginProcessor(ProcessorComponent):
    LAYOUT_ID = 'margin'

    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        config = self.config
        padding_size = int(config.get_white_margin_width() * min(container.get_width(), container.get_height()) / 100)
        padding_img = padding_image(container.get_watermark_img(), padding_size, 'tlr')
        container.update_watermark_img(padding_img)


class SimpleProcessor(ProcessorComponent):
    LAYOUT_ID = 'simple'

    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        ratio = .16 if container.get_ratio() >= 1 else .1
        padding_ratio = .5 if container.get_ratio() >= 1 else .5

        first_text = text_to_image('Shot on',
                                   self.config.get_alternative_font(),
                                   self.config.get_alternative_bold_font(),
                                   is_bold=False,
                                   fill='#212121')
        model = text_to_image(container.get_model().replace(r'/', ' ').replace(r'_', ' '),
                              self.config.get_alternative_font(),
                              self.config.get_alternative_bold_font(),
                              is_bold=True,
                              fill='#D32F2F')
        make = text_to_image(container.get_make().split(' ')[0],
                             self.config.get_alternative_font(),
                             self.config.get_alternative_bold_font(),
                             is_bold=True,
                             fill='#212121')
        first_line = merge_images([first_text, MIDDLE_HORIZONTAL_GAP, model, MIDDLE_HORIZONTAL_GAP, make], 0, 1)
        second_line_text = container.get_param_str() + ', Made by Semi Utils'
        second_line = text_to_image(second_line_text,
                                    self.config.get_alternative_font(),
                                    self.config.get_alternative_bold_font(),
                                    is_bold=False,
                                    fill='#BDBDBD')
        image = merge_images([first_line, MIDDLE_VERTICAL_GAP, second_line], 1, 0)
        height = container.get_height() * ratio * padding_ratio
        image = resize_image_with_height(image, int(height))
        horizontal_padding = int((container.get_width() - image.width) / 2)
        vertical_padding = int((container.get_height() * ratio - image.height) / 2)

        watermark = ImageOps.expand(image, (horizontal_padding, vertical_padding), fill='white')

        watermark_img = merge_images([container.get_watermark_img(), watermark], 1, 1)
        container.update_watermark_img(watermark_img)


class PaddingToOriginalRatioProcessor(ProcessorComponent):
    LAYOUT_ID = 'padding_to_original_ratio'

    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        original_ratio = container.get_original_ratio()
        ratio = container.get_ratio()
        if original_ratio > ratio:
            # 如果原始比例大于当前比例，说明宽度大于高度，需要填充高度
            padding_size = int(container.get_width() / original_ratio - container.get_height())
            padding_img = ImageOps.expand(container.get_watermark_img(), (0, padding_size), fill='white')
        else:
            # 如果原始比例小于当前比例，说明高度大于宽度，需要填充宽度
            padding_size = int(container.get_height() * original_ratio - container.get_width())
            padding_img = ImageOps.expand(container.get_watermark_img(), (padding_size, 0), fill='white')
        container.update_watermark_img(padding_img)


class BackgroundBlurProcessor(ProcessorComponent):
    LAYOUT_ID = 'background_blur'

    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        background = container.get_watermark_img()
        background = background.filter(ImageFilter.GaussianBlur(radius=27))
        background = background.resize((int(container.get_width() * 1.1), int(container.get_height() * 1.1)))
        background.paste(container.get_watermark_img(),
                         (int(container.get_width() * 0.05), int(container.get_height() * 0.05)))
        container.update_watermark_img(background)
