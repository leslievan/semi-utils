# 修改日期格式
import os
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS


def parse_datetime(datetime_string):
    return datetime.strptime(datetime_string, '%Y:%m:%d %H:%M:%S')


def get_file_list(path):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if 'jpg' in file or 'jpeg' in file or 'JPG' in file or 'JPEG' in file:
                file_list.append(file)
    return file_list


def concat_img(img_x, img_y):
    img = Image.new('RGB', (img_x.width, img_x.height + img_y.height), color='white')
    img.paste(img_x, (0, 0))
    img.paste(img_y, (0, img_x.height))
    return img


# 读取 exif 信息，包括相机机型、相机品牌、图片尺寸、镜头焦距、光圈大小、曝光时间、ISO 和拍摄时间
def get_exif(image,full_fram_resolution):
    
    _exif = {}
    info = image._getexif()
    if info:
        _exif['equivalent_focal_length']=0
        for attr, value in info.items():
            decoded_attr = TAGS.get(attr, attr)
            _exif[decoded_attr] = value
        #计算等效焦距
        try:
            if full_fram_resolution[0]:
                if image.size[0]>image.size[1]:
                    imageX=image.size[0]
                    imageY=image.size[1]
                else:
                    imageX=image.size[1]
                    imageY=image.size[0]
                tmp1=full_fram_resolution[0]/imageX
                tmp2=full_fram_resolution[1]/imageY
                _exif['equivalent_focal_length']=_exif['FocalLength']*tmp1 if tmp1<tmp2 else _exif['FocalLength']*tmp2
        except:
            pass #_exif['equivalent_focal_length']=int(_exif['equivalent_focal_length'])
    #print(_exif)
    return _exif


def get_str_from_exif(exif, field):
    if 'id' not in field:
        return ''
    field_id = field.get('id')
    if 'Param' == field_id:
        return get_param_str_from_exif(exif)
    elif 'Date' == field_id:
        try:
            return datetime.strftime(parse_datetime(exif['DateTimeOriginal']), '%Y-%m-%d %H:%M')
        except:
            return ""
    else:
        if field_id in exif:
            return exif[field_id]
        else:
            return ''


def get_param_str_from_exif(exif):
    #print(exif)
    try:
        if int(exif['equivalent_focal_length']):
            focal_length = str(int(exif['FocalLength'])) + '('+str(int(exif['equivalent_focal_length'])) + ')' 'mm'
        else:
            focal_length = str(int(exif['FocalLength'])) + 'mm'
        #print(focal_length)
    except:
        focal_length = ""
    try:
        f_number = 'F' + str(exif['FNumber'])
    except:
        f_number = ""
    try:
        exposure_time = str(exif['ExposureTime'].real)
    except:
        exposure_time = ""
    try:
        iso = 'ISO' + str(exif['ISOSpeedRatings'])
    except:
        iso = ""
    return '  '.join((focal_length, f_number, exposure_time, iso))
