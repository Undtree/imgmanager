from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Image
from .serializers import ImageSerializer
from .utils import get_exif_data, make_thumbnail
from datetime import datetime

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all().order_by('-upload_time')
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # 1. 获取上传文件
        img_file = self.request.data.get('img_url')
        
        # 2. 调用 Utils 处理 EXIF (简化版)
        exif, width, height = get_exif_data(img_file)
        
        # 处理时间格式 (示例)
        shoot_time = None
        if 'shoot_time' in exif:
            try:
                shoot_time = datetime.strptime(exif['shoot_time'], '%Y:%m:%d %H:%M:%S')
            except:
                pass

        # 3. 生成缩略图
        thumb_file = make_thumbnail(img_file)

        # 4. 保存数据库
        serializer.save(
            user=self.request.user,
            width=width,
            height=height,
            file_size=img_file.size / 1024,
            camera_model=exif.get('camera_model'),
            shoot_time=shoot_time,
            thumb_url=thumb_file
        )