from PIL import Image as PilImage
from PIL import ImageOps
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import io
import os
import pillow_heif
from django.core.files.base import ContentFile
from geopy.geocoders import Nominatim

def _convert_to_degrees(value):
    """辅助函数：将 (度, 分, 秒) 元组转换为十进制格式"""
    d = value[0]
    m = value[1]
    s = value[2]
    return d + (m / 60.0) + (s / 3600.0)

pillow_heif.register_heif_opener()

def handle_heic_image(image_file):
    """
    检查是否为 HEIC 文件，如果是，则转换为 JPG 并保留 EXIF。
    如果不是，原样返回。
    """
    # 1. 检查扩展名
    if not image_file.name.lower().endswith(('.heic', '.heif')):
        return image_file

    try:
        # 2. 打开 HEIC 图片
        img = PilImage.open(image_file)
        
        # 3. 转换为 RGB (HEIC 可能是 RGBA)
        img = img.convert('RGB')
        
        # 4. 提取 EXIF 数据 (关键步骤，否则转换后 EXIF 丢失)
        exif_data = img.info.get('exif')

        # 5. 保存为 JPEG 到内存中
        output_io = io.BytesIO()
        save_kwargs = {'format': 'JPEG', 'quality': 100}
        
        # 如果有 EXIF，就带上
        if exif_data:
            save_kwargs['exif'] = exif_data
            
        img.save(output_io, **save_kwargs)
        output_io.seek(0)
        
        # 6. 生成新的文件名 (xxx.heic -> xxx.jpg)
        new_name = image_file.name.rsplit('.', 1)[0] + '.jpg'
        
        # 7. 返回 Django 可识别的文件对象
        return ContentFile(output_io.read(), name=new_name)

    except Exception as e:
        print(f"HEIC 转换失败: {e}")
        return image_file # 如果失败，返回原文件尝试处理
    
def get_address_from_gps(lat, lon):
    try:
        geolocator = Nominatim(user_agent="image_manager_app", timeout=5)
        location = geolocator.reverse(f"{lat}, {lon}", language='zh-cn')
        
        if not location:
            return f"{lat:.4f}, {lon:.4f}"

        addr = location.raw['address']
        
        # 1. 提取省份/直辖市
        state = addr.get('state') or ''
        
        # 2. 提取城市 (地级单位)
        # 优先找 state_district，找不到找 city
        city = addr.get('state_district') or addr.get('city') or ''
        
        # 3. 提取区县 (县级单位)
        # 增加 suburb (社区/郊区) 和 city_district (城市区)
        district = (
            addr.get('county') or 
            addr.get('district') or 
            addr.get('city_district') or 
            addr.get('suburb') or 
            ''
        )
        
        # 4. 提取具体兴趣点 (POI)
        poi = (
            addr.get('building') or 
            addr.get('amenity') or 
            addr.get('tourism') or 
            addr.get('leisure') or 
            addr.get('historic') or 
            addr.get('shop') or 
            addr.get('office') or 
            addr.get('road') or 
            addr.get('village') or 
            ''
        )
        
        # 如果是直辖市 (state 和 city 相同)，去掉 state 避免重复 (如: 北京市北京市)
        if state and city and (state in city or city in state):
            state = ""
        
        # 如果 district 和 city 相同，去掉 district
        if district and city and (district in city):
            district = ""

        # 过滤掉空字符串，用 "·" 或 " " 连接更符合地图展示习惯
        parts = [p for p in [state, city, district, poi] if p]
        full_addr = "-".join(parts)

        return full_addr if full_addr.strip() else location.address

    except Exception as e:
        print(f"地理位置解析失败: {e}")
        return f"{lat:.4f}, {lon:.4f}"

def get_exif_data(image_file):
    """
    提取图片的宽、高以及EXIF信息（拍摄时间、相机型号、GPS经纬度）
    """
    image_file.seek(0)

    try:
        img = PilImage.open(image_file) 
        img.verify() 
        image_file.seek(0)
        img = PilImage.open(image_file)
    except Exception:
        return {}, 0, 0

    exif_data = {}
    
    # 获取 EXIF 对象
    info = img.getexif()
    
    if info:
        # 1. 处理常规 Tag (时间、相机型号)
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            
            if decoded == "DateTimeOriginal":
                try:
                    date_str = str(value).strip().replace('\x00', '')
                    exif_data['shoot_time'] = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except (ValueError, TypeError):
                    exif_data['shoot_time'] = None
            
            elif decoded == "Model":
                exif_data['camera_model'] = str(value).strip()
            
            elif decoded == "ISOSpeedRatings":
                exif_data['iso'] = value
            
            elif decoded == "FNumber":
                # 有些相机返回的是分数，有些是浮点
                exif_data['f_stop'] = float(value) if value else None
                
            elif decoded == "ExposureTime":
                 # 转换为字符串存储快门速度 (如 "1/100")
                exif_data['exposure_time'] = str(value)

        # 2. 专门处理 GPS 数据
        gps_info = info.get_ifd(0x8825)
        
        if gps_info:
            gps_data = {}
            for t, value in gps_info.items():
                sub_decoded = GPSTAGS.get(t, t)
                gps_data[sub_decoded] = value
        
            # 解析经纬度
            if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                try:
                    lat = _convert_to_degrees(gps_data['GPSLatitude'])
                    lon = _convert_to_degrees(gps_data['GPSLongitude'])
                    
                    # 修正南北纬/东西经
                    if gps_data.get('GPSLatitudeRef') == 'S': lat = -lat
                    if gps_data.get('GPSLongitudeRef') == 'W': lon = -lon

                    # 调用之前的逆地理编码函数
                    exif_data['location'] = get_address_from_gps(lat, lon)

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

        # 解决手机竖屏拍照在缩略图中变成横屏的问题
        img = ImageOps.exif_transpose(img)

        if img.width > 4096 or img.height > 4096:
            img.thumbnail((4096, 4096), PilImage.Resampling.LANCZOS)

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