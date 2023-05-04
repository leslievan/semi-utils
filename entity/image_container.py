import logging
import re
from datetime import datetime
from enum import Enum
from pathlib import Path

import piexif
from PIL import Image
from PIL.Image import Transpose
from dateutil import parser

from entity.config import ElementConfig
from enums.constant import CAMERA_MAKE_CAMERA_MODEL_VALUE
from enums.constant import CAMERA_MODEL_LENS_MODEL_VALUE
from enums.constant import CUSTOM_VALUE
from enums.constant import DATETIME_VALUE
from enums.constant import DATE_VALUE
from enums.constant import LENS_MAKE_LENS_MODEL_VALUE
from enums.constant import LENS_VALUE
from enums.constant import MAKE_VALUE
from enums.constant import MODEL_VALUE
from enums.constant import PARAM_VALUE
from enums.constant import TOTAL_PIXEL_VALUE
from utils import calculate_pixel_count
from utils import get_exif


class ExifId(Enum):
    CAMERA_MODEL = 'CameraModelName'
    CAMERA_MAKE = 'Make'
    LENS_MODEL = 'LensModel'
    LENS_MAKE = 'LensMake'
    DATETIME = 'DateTimeOriginal'
    FOCAL_LENGTH = 'FocalLength'
    FOCAL_LENGTH_IN_35MM_FILM = 'FocalLengthIn35mmFormat'
    F_NUMBER = 'FNumber'
    ISO = 'ISO'
    EXPOSURE_TIME = 'ExposureTime'
    SHUTTER_SPEED_VALUE = 'ShutterSpeedValue'
    ORIENTATION = 'Orientation'


PATTERN = re.compile(r"(\d+)\.")  # 匹配小数


class ImageContainer(object):
    def __init__(self, path: Path):
        self.path: Path = path
        self.target_path: Path | None = None
        self.img: Image.Image = Image.open(path)
        self.exif: dict = get_exif(path)
        # 图像信息
        self.original_width = self.img.width
        self.original_height = self.img.height

        self._param_dict = dict()

        # 相机机型
        self.model: str = self.exif[ExifId.CAMERA_MODEL.value] if ExifId.CAMERA_MODEL.value in self.exif else '无'
        # 相机制造商
        self.make: str = self.exif[ExifId.CAMERA_MAKE.value] if ExifId.CAMERA_MAKE.value in self.exif else '无'
        # 镜头型号
        self.lens_model: str = self.exif[ExifId.LENS_MODEL.value] if ExifId.LENS_MODEL.value in self.exif else '无'
        # 镜头制造商
        self.lens_make: str = self.exif[ExifId.LENS_MAKE.value] if ExifId.LENS_MAKE.value in self.exif else '无'
        # 拍摄日期
        try:
            self.date: datetime = parser.parse(self.exif[ExifId.DATETIME.value]) \
                if ExifId.DATETIME.value in self.exif \
                else datetime.now()
        except ValueError as e:
            self.date: datetime = datetime.now()
            logging.exception(f'Error: {self.path}: {str(e)}')
        # 焦距
        try:
            focal_length = PATTERN.search(self.exif[ExifId.FOCAL_LENGTH.value])
            self.focal_length: str = focal_length.group(1) if focal_length else '0'
        except (KeyError, ValueError) as e:
            # 如果转换错误，使用 0
            self.focal_length: str = '0'
            logging.exception(f'Error: {self.path}: {self.exif[ExifId.FOCAL_LENGTH]}: {str(e)}')
        # 等效焦距
        try:
            focal_length_in_35mm_film = PATTERN.search(self.exif[ExifId.FOCAL_LENGTH_IN_35MM_FILM.value])
            self.focal_length_in_35mm_film: str = focal_length_in_35mm_film.group(
                1) if focal_length_in_35mm_film else '0'
        except (KeyError, ValueError) as e:
            # 如果转换错误，使用焦距
            self.focal_length_in_35mm_film: str = self.focal_length
            logging.exception(f'Error: {self.path}: {self.exif[ExifId.FOCAL_LENGTH]}: {str(e)}')

        # 是否使用等效焦距
        self.use_equivalent_focal_length: bool = False
        # 光圈大小
        self.f_number: str = self.exif[ExifId.F_NUMBER.value] if ExifId.F_NUMBER.value in self.exif else '0.0'
        # 曝光时间
        self.exposure_time: str = str(self.exif[ExifId.EXPOSURE_TIME.value]) + 's' \
            if ExifId.EXPOSURE_TIME.value in self.exif else '0s'
        # 感光度
        self.iso: str = self.exif[ExifId.ISO.value] if ExifId.ISO.value in self.exif else '0'
        # 修正图像方向
        self.orientation = self.exif[ExifId.ORIENTATION.value] if ExifId.ORIENTATION.value in self.exif else 1
        if self.orientation == "Rotate 0":
            pass
        elif self.orientation == "Rotate 90 CW":
            self.img = self.img.transpose(Transpose.ROTATE_270)
        elif self.orientation == "Rotate 180":
            self.img = self.img.transpose(Transpose.ROTATE_180)
        elif self.orientation == "Rotate 270 CW":
            self.img = self.img.transpose(Transpose.ROTATE_90)
        else:
            pass

        # 水印设置
        self.custom = '无'
        self.logo = None

        # 水印图片
        self.watermark_img = None

        self._param_dict[TOTAL_PIXEL_VALUE] = calculate_pixel_count(self.original_width, self.original_height)
        self._param_dict[CAMERA_MAKE_CAMERA_MODEL_VALUE] = ' '.join([self.make, self.model])

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
        return datetime.strftime(self.date, '%Y-%m-%d %H:%M')

    def _parse_date(self) -> str:
        """
        解析日期，转换为指定的格式
        :return: 指定格式的日期字符串，转换失败返回原始的时间字符串
        """
        return datetime.strftime(self.date, '%Y-%m-%d')

    def get_attribute_str(self, element: ElementConfig) -> str:
        """
        通过 element 获取属性值
        :param element: element 对象有 name 和 value 两个字段，通过 name 和 value 获取属性值
        :return: 属性值字符串
        """
        if element.get_name() in self._param_dict:
            return self._param_dict[element.get_name()]

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
        elif element.get_name() == CAMERA_MODEL_LENS_MODEL_VALUE:
            return ' '.join([self.model, self.lens_model])
        elif element.get_name() == LENS_MAKE_LENS_MODEL_VALUE:
            return ' '.join([self.lens_make, self.lens_model])
        else:
            return ''

    def get_param_str(self) -> str:
        """
        组合拍摄参数，输出一个字符串
        :return: 拍摄参数字符串
        """
        focal_length = self.focal_length_in_35mm_film if self.use_equivalent_focal_length else self.focal_length
        return ' '.join([str(focal_length) + 'mm', 'f/' + self.f_number, self.exposure_time,
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

    def save(self, target_path, quality=100):
        if self.orientation == "Rotate 0":
            pass
        elif self.orientation == "Rotate 90 CW":
            self.watermark_img = self.watermark_img.transpose(Transpose.ROTATE_90)
        elif self.orientation == "Rotate 180":
            self.watermark_img = self.watermark_img.transpose(Transpose.ROTATE_180)
        elif self.orientation == "Rotate 270 CW":
            self.watermark_img = self.watermark_img.transpose(Transpose.ROTATE_270)
        else:
            pass

        self.watermark_img.save(target_path, quality=quality, encoding='utf-8', exif=self.img.info['exif'])
