from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tb_category'

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    source = models.SmallIntegerField(default=0, help_text="0-人工, 1-AI")

    class Meta:
        db_table = 'tb_tag'

class Image(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, db_table='tb_image_tag', blank=True)
    
    img_url = models.ImageField(upload_to='uploads/%Y/%m/')
    thumb_url = models.ImageField(upload_to='thumbs/%Y/%m/', null=True, blank=True)
    
    # 元数据
    file_size = models.IntegerField(null=True) # KB
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    
    # EXIF 信息
    camera_model = models.CharField(max_length=100, null=True, blank=True)
    shoot_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    
    # 其他属性
    is_public = models.BooleanField(default=True)
    upload_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tb_image'
