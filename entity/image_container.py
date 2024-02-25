import logging
import os
import re
from datetime import datetime
from enum import Enum
from pathlib import Path

from PIL import Image
from PIL.Image import Transpose
from dateutil import parser

from entity.config import ElementConfig
from enums.constant import *
from utils import calculate_pixel_count
from utils import extract_attribute
from utils import get_exif

logger = logging.getLogger(__name__)


class ExifId(Enum):
    CAMERA_MODEL = 'CameraModelName'
    CAMERA_MAKE = 'Make'
    LENS_MODEL = ['LensModel', 'Lens']
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


def get_datetime(exif) -> datetime:
    dt = datetime.now()
    try:
        dt = parser.parse(extract_attribute(exif, ExifId.DATETIME.value,
                                            default_value=str(datetime.now())))
    except ValueError as e:
        logger.info(f'Error: 时间格式错误：{extract_attribute(exif, ExifId.DATETIME.value)}')
    return dt


def get_focal_length(exif):
    focal_length = DEFAULT_VALUE
    focal_length_in_35mm_film = DEFAULT_VALUE

    try:
        focal_lengths = PATTERN.findall(extract_attribute(exif, ExifId.FOCAL_LENGTH.value))
        try:
            focal_length = focal_lengths[0] if focal_length else DEFAULT_VALUE
        except IndexError as e:
            logger.info(
                f'ValueError: 不存在焦距：{focal_lengths} : {e}')
        try:
            focal_length_in_35mm_film: str = focal_lengths[1] if focal_length else DEFAULT_VALUE
        except IndexError as e:
            logger.info(f'ValueError: 不存在 35mm 焦距：{focal_lengths} : {e}')
    except Exception as e:
        logger.info(f'KeyError: 焦距转换错误：{extract_attribute(exif, ExifId.FOCAL_LENGTH.value)} : {e}')

    return focal_length, focal_length_in_35mm_film


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

        self.model: str = extract_attribute(self.exif, ExifId.CAMERA_MODEL.value)
        self.make: str = extract_attribute(self.exif, ExifId.CAMERA_MAKE.value)
        self.lens_model: str = extract_attribute(self.exif, *ExifId.LENS_MODEL.value)
        self.lens_make: str = extract_attribute(self.exif, ExifId.LENS_MAKE.value)
        self.date: datetime = get_datetime(self.exif)
        self.focal_length, self.focal_length_in_35mm_film = get_focal_length(self.exif)
        self.f_number: str = extract_attribute(self.exif, ExifId.F_NUMBER.value, default_value=DEFAULT_VALUE)
        self.exposure_time: str = extract_attribute(self.exif, ExifId.EXPOSURE_TIME.value, default_value=DEFAULT_VALUE,
                                                    suffix='s')
        self.iso: str = extract_attribute(self.exif, ExifId.ISO.value, default_value=DEFAULT_VALUE)

        # 是否使用等效焦距
        self.use_equivalent_focal_length: bool = False

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

        self._param_dict[MODEL_VALUE] = self.model
        self._param_dict[PARAM_VALUE] = self.get_param_str()
        self._param_dict[MAKE_VALUE] = self.make
        self._param_dict[DATETIME_VALUE] = self._parse_datetime()
        self._param_dict[DATE_VALUE] = self._parse_date()
        self._param_dict[LENS_VALUE] = self.lens_model
        filename_without_ext = os.path.splitext(self.path.name)[0]
        self._param_dict[FILENAME_VALUE] = filename_without_ext
        self._param_dict[TOTAL_PIXEL_VALUE] = calculate_pixel_count(self.original_width, self.original_height)

        self._param_dict[CAMERA_MAKE_CAMERA_MODEL_VALUE] = ' '.join(
            [self._param_dict[MAKE_VALUE], self._param_dict[MODEL_VALUE]])
        self._param_dict[LENS_MAKE_LENS_MODEL_VALUE] = ' '.join(
            [self.lens_make, self._param_dict[LENS_VALUE]])
        self._param_dict[CAMERA_MODEL_LENS_MODEL_VALUE] = ' '.join(
            [self._param_dict[MODEL_VALUE], self._param_dict[LENS_VALUE]])
        self._param_dict[DATE_FILENAME_VALUE] = ' '.join(
            [self._param_dict[DATE_VALUE], self._param_dict[FILENAME_VALUE]])
        self._param_dict[DATETIME_FILENAME_VALUE] = ' '.join(
            [self._param_dict[DATETIME_VALUE], self._param_dict[FILENAME_VALUE]])

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
        if element.get_name() == CUSTOM_VALUE:
            self.custom = element.get_value()
            return self.custom
        elif element.get_name() in self._param_dict:
            return self._param_dict[element.get_name()]
        else:
            return ''

    def get_param_str(self) -> str:
        """
        组合拍摄参数，输出一个字符串
        :return: 拍摄参数字符串
        """
        focal_length = self.focal_length_in_35mm_film if self.use_equivalent_focal_length else self.focal_length
        return '  '.join([str(focal_length) + 'mm', 'f/' + self.f_number, self.exposure_time,
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
        if self.watermark_img == watermark_img:
            return
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

        if self.watermark_img.mode != 'RGB':
            self.watermark_img = self.watermark_img.convert('RGB')

        if 'exif' in self.img.info:
            self.watermark_img.save(target_path, quality=quality, encoding='utf-8',
                                    exif=self.img.info['exif'] if 'exif' in self.img.info else '')
        else:
            self.watermark_img.save(target_path, quality=quality, encoding='utf-8')
