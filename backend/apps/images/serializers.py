from rest_framework import serializers
from .models import Image, Tag

class ImageSerializer(serializers.ModelSerializer):
    uploader_name = serializers.CharField(source='user.username', read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ('user', 'thumb_url', 'width', 'height', 'camera_model', 'shoot_time')