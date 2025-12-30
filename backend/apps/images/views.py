from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Image, Tag, Category
from .serializers import ImageSerializer, TagSerializer, CategorySerializer
from .utils import get_exif_data, make_thumbnail
from PIL import Image as PilImage 

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        实现多维检索逻辑
        支持参数: ?q=关键词 & category=id & start_date=...
        支持 ?only_my=true 参数
        """
        queryset = Image.objects.all().select_related('user', 'category').prefetch_related('tags')
        
        # 基础过滤：只能看公开的，或者是自己上传的
        user = self.request.user
        if user.is_authenticated:
            # 逻辑：公开的 OR 自己的
            queryset = queryset.filter(Q(is_public=True) | Q(user=user))
        else:
            queryset = queryset.filter(is_public=True)

        only_my = self.request.query_params.get('only_my')

        if only_my == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        # 搜索逻辑
        search_query = self.request.query_params.get('q', None)
        category_id = self.request.query_params.get('category', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if start_date:
            queryset = queryset.filter(shoot_time__gte=start_date)

        if search_query:
            # SELECT * WHERE tag IN (...)
            # 这里扩展为：匹配标签名 OR 匹配描述 OR 匹配地点
            queryset = queryset.filter(
                Q(tags__name__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(camera_model__icontains=search_query)
            ).distinct()

        return queryset.order_by('-upload_time')

    def perform_create(self, serializer):
        img_file = self.request.data.get('img_url')
        
        # 提取 EXIF
        exif_data, width, height = get_exif_data(img_file)
        
        # 生成缩略图
        thumb_file = make_thumbnail(img_file)

        # 清理不需要存入 extra_kwargs 的字段
        exif_data.pop('width', None)
        exif_data.pop('height', None)
        
        # [重要] 最后一次重置指针，为了 Django 的保存操作
        if img_file:
            img_file.seek(0)

        # [重要] 显式指定 img_url=img_file，确保使用的是当前这个指针归零的对象
        serializer.save(
            user=self.request.user,
            img_url=img_file, 
            width=width,
            height=height,
            file_size=int(img_file.size / 1024),
            thumb_url=thumb_file,
            **exif_data
        )

    def perform_update(self, serializer):
        new_img = self.request.data.get('img_url', None)
        
        # 如果上传了新文件
        if new_img and hasattr(new_img, 'read'):
             thumb_file = make_thumbnail(new_img)
             
             # [修复 Bug] 这里不能用 Image.open，因为 Image 是 Django 模型
             # 必须用 PilImage (from PIL import Image as PilImage)
             new_img.seek(0)
             pil_img = PilImage.open(new_img)
             
             # 获取新尺寸
             width, height = pil_img.width, pil_img.height
             
             # 同样记得重置指针
             new_img.seek(0)
             
             serializer.save(
                 img_url=new_img, # 显式传递
                 width=width, 
                 height=height,
                 file_size=int(new_img.size / 1024),
                 thumb_url=thumb_file
             )
        else:
            serializer.save()