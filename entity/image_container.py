from datetime import datetime

from PIL import Image
from PIL.Image import Transpose

from utils import get_exif


class ImageContainer(object):
    def __init__(self, path):
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
        self.focal_length = int(self.exif['FocalLength']) if 'FocalLength' in self.exif else 0
        # 等效焦距
        self.focal_length_in_35mm_film = int(self.exif['FocalLengthIn35mmFilm']) \
            if 'FocalLengthIn35mmFilm' in self.exif else self.focal_length
        # 是否使用等效焦距
        self.use_equivalent_focal_length = False
        # 光圈大小
        self.f_number = float(self.exif['FNumber']) if 'FNumber' in self.exif else .0
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

        # 水印设置
        self.custom = '无'
        self.logo = None

        # 图像信息
        self.original_width = self.exif['ExifImageWidth'] if 'ExifImageWidth' in self.exif else 0
        self.original_length = self.exif['ExifImageHeight'] if 'ExifImageHeight' in self.exif else 0
        self.width = self.img.width
        self.height = self.img.height
        self.ratio = self.width / self.height

        # 水印图片
        self.watermark_img = None

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

    def get_attribute_str(self, element) -> str:
        """
        通过 element 获取属性值
        :param element: element 对象有 name 和 value 两个字段，通过 name 和 value 获取属性值
        :return: 属性值字符串
        """
        if element is None or element.get_name() == '':
            return ''
        if element.get_name() == 'Model':
            return self.model
        elif element.get_name() == 'Param':
            return self.get_param_str()
        elif element.get_name() == 'Make':
            return self.make
        elif element.get_name() == 'Date':
            return self._parse_datetime()
        elif element.get_name() == 'LensModel':
            return self.lens_model
        elif element.get_name() == 'Custom':
            self.custom = element.value
            return self.custom
        else:
            return ''

    def get_param_str(self) -> str:
        """
        组合拍摄参数，输出一个字符串
        :return: 拍摄参数字符串
        """
        focal_length = self.focal_length_in_35mm_film if self.use_equivalent_focal_length else self.focal_length
        return '  '.join([str(focal_length) + 'mm', 'f/' + str(self.f_number), self.exposure_time,
                          'ISO' + str(self.iso)])

    def get_original_ratio(self):
        return self.original_width / self.original_length

    def get_logo(self):
        return self.logo

    def set_logo(self, logo) -> None:
        self.logo = logo

    def is_use_equivalent_focal_length(self, flag: bool) -> None:
        self.use_equivalent_focal_length = flag

    def close(self):
        self.img.close()
