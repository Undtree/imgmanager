from django.contrib import admin
from .models import Image, Tag, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'create_time')
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'source')
    list_filter = ('source',) # 侧边栏过滤器：按来源筛选
    search_fields = ('name',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    # 列表页显示的字段
    list_display = ('id', 'user', 'category', 'camera_model', 'shoot_time', 'is_public', 'upload_time')
    # 侧边栏过滤器
    list_filter = ('is_public', 'upload_time', 'category')
    # 搜索框
    search_fields = ('camera_model', 'location', 'user__username')
    # 在详情页中，tags 是多对多字段，默认显示比较简陋，使用 filter_horizontal 优化显示
    filter_horizontal = ('tags',)
    # 只读字段（防止管理员手动瞎改 EXIF 数据）
    readonly_fields = ('width', 'height', 'file_size', 'camera_model', 'shoot_time', 'location', 'iso', 'f_stop', 'exposure_time')