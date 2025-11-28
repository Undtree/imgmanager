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
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category', 
        write_only=True,
        required=False,
        allow_null=True
    )
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ('user', 'thumb_url', 'width', 'height', 'camera_model', 'shoot_time', 'location', 'file_size', 'iso', 'f_stop', 'exposure_time')

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        # 创建图片实例
        image = Image.objects.create(**validated_data)
        
        # 处理标签：如果存在则获取，不存在则创建
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name, defaults={'source': 0})
            image.tags.add(tag)
        
        return image

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        
        # 标准更新
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新标签 (覆盖式)
        if tag_names is not None:
            instance.tags.clear()
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                instance.tags.add(tag)
                
        return instance