import string
from datetime import datetime

from PIL import Image
from PIL.Image import Transpose

from utils import get_exif

printable = set(string.printable)


class ImageContainer(object):
    def __init__(self, path):
        self.img = Image.open(path)
        self.exif = get_exif(self.img)

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

    def _parse_datetime(self):
        try:
            date = datetime.strptime(self.date, '%Y:%m:%d %H:%M:%S')
            return datetime.strftime(date, '%Y-%m-%d %H:%M')
        except ValueError:
            return '无'

    def get_attribute_str(self, element):
        if element is None or element.name == '':
            return ''
        if element.name == 'Model':
            return self.model
        elif element.name == 'Param':
            return self.get_param_str()
        elif element.name == 'Make':
            return self.make
        elif element.name == 'Date':
            return self._parse_datetime()
        elif element.name == 'LensModel':
            return self.lens_model
        elif element.name == 'Custom':
            self.custom = element.value
            return self.custom
        else:
            return ''

    def get_param_str(self):
        focal_length = self.focal_length_in_35mm_film if self.use_equivalent_focal_length else self.focal_length
        return '  '.join([str(focal_length) + 'mm', 'f/' + str(self.f_number), self.exposure_time,
                          'ISO' + str(self.iso)])

    def get_original_ratio(self):
        return self.original_width / self.original_length

    def get_logo(self):
        return self.logo

    def set_logo(self, logo):
        self.logo = logo

    def close(self):
        self.img.close()
