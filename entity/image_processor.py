import string

from PIL import Image
from PIL import ImageFilter
from PIL import ImageOps

from entity.config import Config
from entity.image_container import ImageContainer
from utils import append_image_by_side
from utils import concatenate_image
from utils import padding_image
from utils import resize_image_with_width
from utils import square_image
from utils import text_to_image

printable = set(string.printable)

GRAY = '#CBCBC9'
NORMAL_HEIGHT = 1000


class ProcessorComponent:
    """
    图片处理器组件
    """
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
    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        pass


class ShadowProcessor(ProcessorComponent):
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
    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        image = container.get_watermark_img()
        container.update_watermark_img(square_image(image, auto_close=False))


class WatermarkProcessor(ProcessorComponent):
    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        """
        生成一个默认布局的水印图片
        :param container: 图片对象
        :return: 添加水印后的图片对象
        """
        config = self.config

        ratio = .1 if container.get_ratio() >= 1 else .13
        padding_ratio = .44 if container.get_ratio() >= 1 else .618

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
    def __init__(self, config: Config):
        self.config = config

    def process(self, container: ImageContainer) -> None:
        config = self.config
        padding_size = int(config.get_white_margin_width() * min(container.get_width(), container.get_height()) / 100)
        padding_img = padding_image(container.get_watermark_img(), padding_size, 'tlr')
        container.update_watermark_img(padding_img)
