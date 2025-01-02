from rest_framework import serializers
from .models import Image, Tag, Category

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
    category_id = serializers.CharField(
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

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        # 创建图片实例
        image_data = {**validated_data}
        cat_name = validated_data.pop('category_id', None)

        if cat_name:
            # 存在则获取，不存在则创建
            category, _ = Category.objects.get_or_create(name=cat_name)
            image_data['category'] = category
        else:
            image_data['category'] = None

        image = Image.objects.create(**image_data)

        # 处理标签；如果存在则获取，不存在则创建
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name, defaults={'source': 0})
            image.tags.add(tag)
        
        return image

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        cat_name = validated_data.pop('category_id', None)
        
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