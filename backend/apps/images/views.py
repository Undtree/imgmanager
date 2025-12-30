from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Image, Tag, Category
from .serializers import ImageSerializer, TagSerializer, CategorySerializer
from .utils import get_exif_data, make_thumbnail

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
        """
        queryset = Image.objects.all().select_related('user', 'category').prefetch_related('tags')
        
        # 1. 基础过滤：只能看公开的，或者是自己上传的
        user = self.request.user
        if user.is_authenticated:
            # 逻辑：公开的 OR 自己的
            queryset = queryset.filter(Q(is_public=True) | Q(user=user))
        else:
            queryset = queryset.filter(is_public=True)

        # 2. 搜索逻辑
        search_query = self.request.query_params.get('q', None)
        category_id = self.request.query_params.get('category', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        if start_date:
            queryset = queryset.filter(shoot_time__gte=start_date)

        if search_query:
            # 报告要求的逻辑：SELECT * WHERE tag IN (...)
            # 这里扩展为：匹配标签名 OR 匹配描述 OR 匹配地点
            queryset = queryset.filter(
                Q(tags__name__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(camera_model__icontains=search_query)
            ).distinct()

        return queryset.order_by('-upload_time')

    def perform_create(self, serializer):
        # 获取上传的文件对象
        img_file = self.request.data.get('img_url')
        
        # 1. 提取 EXIF
        exif_data, width, height = get_exif_data(img_file)
        
        # 2. 生成缩略图
        thumb_file = make_thumbnail(img_file)

        exif_data.pop('width', None)
        exif_data.pop('height', None)
        
        # 3. 保存
        serializer.save(
            user=self.request.user,
            width=width,
            height=height,
            file_size=int(img_file.size / 1024),
            thumb_url=thumb_file,
            **exif_data # 解包 exif 字典: camera_model, shoot_time, location 等
        )

    def perform_update(self, serializer):
        """
        处理编辑功能的保存（如裁剪后）
        如果是重新上传了图片(img_url变了)，则需要重新生成缩略图和更新信息
        """
        instance = serializer.instance
        new_img = self.request.data.get('img_url', None)
        
        # 如果是一个文件对象（说明上传了新图/剪裁后的图）
        if new_img and hasattr(new_img, 'read'):
             # 重新生成缩略图
             thumb_file = make_thumbnail(new_img)
             # 更新元数据 (裁剪后大小可能变化)
             img = Image.open(new_img)
             serializer.save(
                 width=img.width, 
                 height=img.height,
                 file_size=int(new_img.size / 1024),
                 thumb_url=thumb_file
             )
        else:
            serializer.save()