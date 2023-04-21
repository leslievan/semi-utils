from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.Image import Transpose

from entity.config import ElementConfig
from enums.constant import CUSTOM_VALUE
from enums.constant import DATETIME_VALUE
from enums.constant import DATE_VALUE
from enums.constant import LENS_VALUE
from enums.constant import MAKE_VALUE
from enums.constant import MODEL_VALUE
from enums.constant import PARAM_VALUE
from utils import get_exif


class ImageContainer(object):
    def __init__(self, path: Path):
        self.img = Image.open(path)
        self.exif = get_exif(path)

        # 相机机型
        self.model = self.exif['Model'] if 'Model' in self.exif else '无'
        # 相机制造商
        self.make = self.exif['Make'] if 'Make' in self.exif else '无'
        # 镜头型号
        self.lens_model = self.exif['LensModel'] if 'LensModel' in self.exif else '无'
        # 拍摄日期
        self.date = self.exif['DateTimeOriginal'] \
            if 'DateTimeOriginal' in self.exif \
            else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 焦距
        try:
            self.focal_length = int(self.exif['FocalLength']) if 'FocalLength' in self.exif else 0
        except ValueError:
            self.focal_length = 0
        # 等效焦距
        try:
            self.focal_length_in_35mm_film = int(self.exif['FocalLengthIn35mmFilm']) \
                if 'FocalLengthIn35mmFilm' in self.exif else self.focal_length
        except ValueError:
            self.focal_length_in_35mm_film = self.focal_length
        # 是否使用等效焦距
        self.use_equivalent_focal_length = False
        # 光圈大小
        try:
            self.f_number = float(self.exif['FNumber']) if 'FNumber' in self.exif else .0
        except:
            self.f_number = .0
        # 曝光时间
        self.exposure_time = str(self.exif['ExposureTime'].real) \
            if 'ExposureTime' in self.exif else '0s'
        # 感光度
        self.iso = self.exif['ISOSpeedRatings'] if 'ISOSpeedRatings' in self.exif else 0

        # 修正图像方向
        self.orientation = self.exif['Orientation'] if 'Orientation' in self.exif else 0
        if self.orientation == 3:
            self.img = self.img.transpose(Transpose.ROTATE_180)
        elif self.orientation == 6:
            self.img = self.img.transpose(Transpose.ROTATE_270)
        elif self.orientation == 8:
            self.img = self.img.transpose(Transpose.ROTATE_90)
        self.exif['Orientation'] = 1

        # 水印设置
        self.custom = '无'
        self.logo = None

        # 图像信息
        self.original_width = self.img.width
        self.original_height = self.img.height

        # 水印图片
        self.watermark_img = None

    def get_height(self):
        return self.get_watermark_img().height

    def get_width(self):
        return self.get_watermark_img().width

    def get_model(self):
        return self.model

    def get_make(self):
        return self.make

    def get_ratio(self):
        return self.img.width / self.img.height

    def get_img(self):
        return self.img

    def _parse_datetime(self) -> str:
        """
        解析日期，转换为指定的格式
        :return: 指定格式的日期字符串，转换失败返回原始的时间字符串
        """
        try:
            date = ''.join(filter(lambda x: x.isprintable(), self.date))
            date = datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
            return datetime.strftime(date, '%Y-%m-%d %H:%M')
        except ValueError:
            return self.date

    def _parse_date(self) -> str:
        """
        解析日期，转换为指定的格式
        :return: 指定格式的日期字符串，转换失败返回原始的时间字符串
        """
        try:
            date = ''.join(filter(lambda x: x.isprintable(), self.date))
            date = datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
            return datetime.strftime(date, '%Y-%m-%d')
        except ValueError:
            return self.date

    def get_attribute_str(self, element: ElementConfig) -> str:
        """
        通过 element 获取属性值
        :param element: element 对象有 name 和 value 两个字段，通过 name 和 value 获取属性值
        :return: 属性值字符串
        """
        if element is None or element.get_name() == '':
            return ''
        if element.get_name() == MODEL_VALUE:
            return self.model
        elif element.get_name() == PARAM_VALUE:
            return self.get_param_str()
        elif element.get_name() == MAKE_VALUE:
            return self.make
        elif element.get_name() == DATETIME_VALUE:
            return self._parse_datetime()
        elif element.get_name() == DATE_VALUE:
            return self._parse_date()
        elif element.get_name() == LENS_VALUE:
            return self.lens_model
        elif element.get_name() == CUSTOM_VALUE:
            self.custom = element.get_value()
            return self.custom
        else:
            return ''

    def get_param_str(self) -> str:
        """
        组合拍摄参数，输出一个字符串
        :return: 拍摄参数字符串
        """
        focal_length = self.focal_length_in_35mm_film if self.use_equivalent_focal_length else self.focal_length
        return ' '.join([str(focal_length) + 'mm', 'f/' + str(self.f_number), self.exposure_time,
                          'ISO' + str(self.iso)])

    def get_original_height(self):
        return self.original_height

    def get_original_width(self):
        return self.original_width

    def get_original_ratio(self):
        return self.original_width / self.original_height

    def get_logo(self):
        return self.logo

    def set_logo(self, logo) -> None:
        self.logo = logo

    def is_use_equivalent_focal_length(self, flag: bool) -> None:
        self.use_equivalent_focal_length = flag

    def get_watermark_img(self) -> Image.Image:
        if self.watermark_img is None:
            self.watermark_img = self.img.copy()
        return self.watermark_img

    def update_watermark_img(self, watermark_img) -> None:
        original_watermark_img = self.watermark_img
        self.watermark_img = watermark_img
        if original_watermark_img is not None:
            original_watermark_img.close()

    def close(self):
        self.img.close()
        self.watermark_img.close()
