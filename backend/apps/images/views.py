from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Image, Tag, Category
from .serializers import ImageSerializer, TagSerializer, CategorySerializer
from .utils import get_exif_data, make_thumbnail
from .ai_utils import classify_image
from PIL import Image as PilImage 
import jieba

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
                Q(category__name__icontains=search_query) |
                Q(camera_model__icontains=search_query)
            ).distinct()

        return queryset.order_by('-upload_time')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='analyze')
    def analyze(self, request):
        """
        接收图片，返回 AI 识别建议的标签
        URL: POST /api/images/analyze/
        """
        img_file = request.FILES.get('img_url') # 前端传文件的字段名
        if not img_file:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if hasattr(img_file, 'seek'):
            img_file.seek(0)
        # 调用本地 AI
        tags = classify_image(img_file)
        
        return Response({"suggested_tags": tags})

    def perform_update(self, serializer):        
        serializer.save()

class MCPView(APIView):
    """
    MCP 协议接口
    URL: GET /api/mcp/search?q=...
    """
    permission_classes = [permissions.IsAuthenticated] # 允许外部 Agent 访问

    def get(self, request):
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({"status": "error", "msg": "Query is empty"})

        # 中文分词
        # 定义“停用词”：这些词对搜索没有帮助，应该过滤掉
        STOP_WORDS = {
            "找", "一下", "帮我", "的", "照片", "图片", "图", "有没有", 
            "搜索", "查看", "显示", "里", "关于", "啊", "呀", "呢"
        }

        # 使用 jieba 搜索引擎模式分词
        # 例如："帮我找一下海边的照片" -> ['帮我', '找', '一下', '海边', '的', '照片']
        seg_list = jieba.lcut_for_search(query)
        
        # 过滤掉停用词，只保留关键词
        keywords = [word for word in seg_list if word not in STOP_WORDS and len(word.strip()) > 0]
        
        print(f"原始查询: {query}, 提取关键词: {keywords}") # 用于调试

        # 如果分词后没东西了（用户只输入了“照片”），则不返回结果，防止返回全库
        if not keywords:
             return Response({
                "status": "success",
                "results": [],
                "msg": "未提取到有效关键词"
            })

        # 构建查询
        q_obj = Q()
        for k in keywords:
            # 只要匹配到一个关键词即可 (OR 逻辑)
            # 匹配 标签、分类、描述、地点、相机型号
            q_obj |= Q(tags__name__icontains=k)
            q_obj |= Q(category__name__icontains=k)
            q_obj |= Q(location__icontains=k)
            q_obj |= Q(camera_model__icontains=k)

        # 只查当前用户可见的图片 (公开 OR 自己的)
        base_qs = Image.objects.filter(Q(is_public=True) | Q(user=request.user))
        
        # 应用搜索条件
        images = base_qs.filter(q_obj).distinct().order_by('-upload_time')[:10]

        results = []
        for img in images:
            tag_names = ",".join([t.name for t in img.tags.all()])
            desc = f"拍摄于:{img.shoot_time}, 标签:{tag_names}"
            
            results.append({
                "id": img.id,
                "url": request.build_absolute_uri(img.img_url.url),
                "description": desc,
                "score": 1.0
            })

        return Response({
            "status": "success",
            "results": results,
            "keywords": keywords # 可以返回关键词给前端展示，显得更智能
        })