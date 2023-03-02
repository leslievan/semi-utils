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

        self.model = self.exif['Model'] if 'Model' in self.exif else 'Unknown Model'
        self.make = self.exif['Make'] if 'Make' in self.exif else 'Unknown Make'
        self.lens_model = self.exif['LensModel'] if 'LensModel' in self.exif else 'Unknown LensModel'
        self.model = ''.join(filter(lambda x: x in printable, self.model))
        self.make = ''.join(filter(lambda x: x in printable, self.make))
        self.lens_model = ''.join(filter(lambda x: x in printable, self.lens_model))
        self.date = self.exif['DateTimeOriginal'] if 'DateTimeOriginal' in self.exif else datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')
        self.focal_length = int(self.exif['FocalLength']) if 'FocalLength' in self.exif else 0
        self.f_number = int(self.exif['FNumber']) if 'FNumber' in self.exif else 0
        self.exposure_time = str(
            self.exif['ExposureTime'].real) if 'ExposureTime' in self.exif else 'Unknown ExposureTime'
        self.iso = self.exif['ISOSpeedRatings'] if 'ISOSpeedRatings' in self.exif else 0

        self.orientation = self.exif['Orientation'] if 'Orientation' in self.exif else 0
        if self.orientation == 3:
            self.img = self.img.transpose(Transpose.ROTATE_180)
        elif self.orientation == 6:
            self.img = self.img.transpose(Transpose.ROTATE_270)
        elif self.orientation == 8:
            self.img = self.img.transpose(Transpose.ROTATE_90)

        self.custom = 'Unknown'
        self.logo = None

        self.original_width = self.exif['ExifImageWidth'] if 'ExifImageWidth' in self.exif else 0
        self.original_length = self.exif['ExifImageHeight'] if 'ExifImageHeight' in self.exif else 0
        self.width = self.img.width
        self.height = self.img.height
        self.ratio = self.width / self.height

        self.watermark_img = None

    def _parse_datetime(self):
        try:
            date = datetime.strptime(self.date, '%Y:%m:%d %H:%M:%S')
            return datetime.strftime(date, '%Y-%m-%d %H:%M')
        except ValueError:
            return 'Unknown Date'

    def get_attribute_str(self, element):
        if element is None or element.name == '':
            return ''
        if element.name == 'Model':
            return self.model
        elif element.name == 'Param':
            return self.get_param_str()
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
        return '  '.join([str(self.focal_length) + 'mm', 'F' + "{:2.1f}".format(self.f_number), self.exposure_time,
                          'ISO' + str(self.iso)])

    def get_original_ratio(self):
        return self.original_width / self.original_length

    def get_logo(self):
        return self.logo

    def set_logo(self, logo):
        self.logo = logo

    def close(self):
        self.img.close()
