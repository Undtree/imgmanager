from rest_framework import serializers
from .models import Image, Tag, Category
from .utils import handle_heic_image, get_exif_data, make_thumbnail

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'source']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    uploader_name = serializers.CharField(source='user.username', read_only=True)
    # 读取时显示详细的 Tag 对象，写入时接收 Tag 名称列表
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=30), 
        write_only=True, 
        required=False
    )
    category_upload = serializers.CharField(
        allow_blank=True, 
        write_only=True,
        required=False,
        allow_null=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ('user', 'category', 'thumb_url', 'width', 'height', 'camera_model', 'shoot_time', 'location', 'file_size', 'iso', 'f_stop', 'exposure_time')

    def validate_img_url(self, value):
        """
        在字段验证阶段拦截图片。
        如果是 HEIC，这里会把它变成 JPG 对象。
        """
        # 调用工具函数处理
        value = handle_heic_image(value)
        
        # 将这些额外数据挂载到文件对象上，方便 create() 调用
        value.seek(0)
        return value
    
    def create(self, validated_data):
        print(f"DEBUG: 最终准备保存的文件名是: {validated_data['img_url'].name}")
        img_file = validated_data.get('img_url')
        
        tag_names = validated_data.pop('tag_names', [])
        cat_name = validated_data.pop('category_upload', None)
        
        # 合并 EXIF 数据到验证数据中
        if hasattr(img_file, 'seek'): img_file.seek(0)
        exif_info, width, height = get_exif_data(img_file)
        
        if hasattr(img_file, 'seek'): img_file.seek(0)
        thumb_file = make_thumbnail(img_file)
        
        # 4. 将提取的数据补充进 validated_data
        # 即使 get_exif_data 返回 None，get() 也会处理，不会报错
        validated_data.update({
            'width': width,
            'height': height,
            'file_size': int(img_file.size / 1024),
            'thumb_url': thumb_file,
            'camera_model': exif_info.get('camera_model'),
            'shoot_time': exif_info.get('shoot_time'),
            'location': exif_info.get('location'),
            'iso': exif_info.get('iso'),
            'f_stop': exif_info.get('f_stop'),
            'exposure_time': exif_info.get('exposure_time'),
        })
        
        if cat_name:
            # 存在则获取，不存在则创建
            category, _ = Category.objects.get_or_create(name=cat_name)
            validated_data['category'] = category
        else:
            validated_data['category'] = None

        if hasattr(img_file, 'seek'): img_file.seek(0)
        image = Image.objects.create(**validated_data)

        # 处理标签；如果存在则获取，不存在则创建
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name, defaults={'source': 0})
            image.tags.add(tag)
        
        return image

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        cat_name = validated_data.pop('category_upload', None)
        
        # 更新相册
        if cat_name == "":
            instance.category = None
        elif cat_name:
            category, _ = Category.objects.get_or_create(name=cat_name)
            instance.category = category

        # 标准更新
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 更新标签 (覆盖式)
        if tag_names is not None:
            instance.tags.clear()
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                instance.tags.add(tag)
                
        instance.save()
        return instance