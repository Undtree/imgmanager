from PIL import Image as PilImage
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import io
import os
from django.core.files.base import ContentFile

def _convert_to_degrees(value):
    """辅助函数：将 (度, 分, 秒) 元组转换为十进制格式"""
    d = value[0]
    m = value[1]
    s = value[2]
    return d + (m / 60.0) + (s / 3600.0)

def get_exif_data(image_file):
    """
    提取图片的宽、高以及EXIF信息（拍摄时间、相机型号、GPS经纬度）
    """
    image_file.seek(0)

    try:
        img = PilImage.open(image_file) 
        img.verify() # 验证文件完整性，但这可能会移动指针
        
        # verify() 后需要重新 open 才能读取数据，Pillow 的特性
        image_file.seek(0)
        img = PilImage.open(image_file)
    except Exception:
        # 如果不是图片，直接返回
        return {}, 0, 0

    exif_data = {}
    
    # 尝试获取 EXIF 数据 (PNG 等格式可能没有)
    info = img._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            
            if decoded == "DateTimeOriginal":
                # 格式通常是 YYYY:MM:DD HH:MM:SS，需要转换为 YYYY-MM-DD HH:MM:SS
                try:
                    # 强制转为字符串并清洗：去除首尾空格和不可见的 \x00 空字符
                    date_str = str(value).strip().replace('\x00', '')
                    
                    # 尝试将 EXIF 格式转为 Python datetime 对象
                    exif_data['shoot_time'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except (ValueError, TypeError):
                    # 如果解析失败就设为 None，防止报错
                    exif_data['shoot_time'] = None
            elif decoded == "Model":
                exif_data['camera_model'] = str(value).strip()
            elif decoded == "ISOSpeedRatings":
                exif_data['iso'] = value
            elif decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
            
                # 解析经纬度
                if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                    try:
                        lat = _convert_to_degrees(gps_data['GPSLatitude'])
                        lon = _convert_to_degrees(gps_data['GPSLongitude'])
                        
                        # 修正南北纬/东西经
                        # GPSLatitudeRef: 'N' or 'S'
                        if gps_data.get('GPSLatitudeRef') == 'S': lat = -lat
                        # GPSLongitudeRef: 'E' or 'W'
                        if gps_data.get('GPSLongitudeRef') == 'W': lon = -lon
                        
                        exif_data['location'] = f"{lat:.4f}, {lon:.4f}" 
                    except Exception as e:
                        print(f"GPS parsing error: {e}")

    return exif_data, img.width, img.height

def make_thumbnail(image_file, size=(300, 300)):
    """
    生成缩略图
    :param image_file: 原始图片文件对象
    :param size: 缩略图最大尺寸 (宽, 高)
    :return: Django ContentFile 对象
    """
    image_file.seek(0)
    
    try: 
        img = PilImage.open(image_file)
        # 如果图片是 RGBA (如 PNG)，转换为 RGB，否则保存为 JPEG 会报错
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # 保持比例缩放
        img.thumbnail(size)

        # 将图片保存到内存中
        thumb_io = io.BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        # 生成文件名 (例如: original_thumb.jpg)
        name = image_file.name
        if not name:
            name = 'image.jpg'
        base_name, _ = os.path.splitext(name)
        thumb_name = f"{base_name}_thumb.jpg"

        return ContentFile(thumb_io.getvalue(), name=thumb_name)
    except Exception as e:
        print(f"缩略图生成失败: {e}")
        return None