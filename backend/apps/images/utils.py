from PIL import Image as PilImage
from PIL.ExifTags import TAGS, GPSTAGS
import io
from django.core.files.base import ContentFile

def get_exif_data(image_file):
    """提取EXIF信息：拍摄时间、相机型号、GPS等"""
    img = PilImage.open(image_file)
    exif_data = {}
    info = img._getexif()
    
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "DateTimeOriginal":
                exif_data['shoot_time'] = value # 需格式化 "YYYY:MM:DD HH:MM:SS"
            elif decoded == "Model":
                exif_data['camera_model'] = value
            # GPS处理较复杂，需转换度分秒，此处简化处理
    
    return exif_data, img.width, img.height

def make_thumbnail(image_file, size=(300, 300)):
    """生成缩略图"""
    img = PilImage.open(image_file)
    img.convert('RGB')
    img.thumbnail(size)
    
    thumb_io = io.BytesIO()
    img.save(thumb_io, 'JPEG', quality=85)
    
    return ContentFile(thumb_io.getvalue(), name=image_file.name)