from rest_framework import serializers
from .models import User
import re

class UserSerializer(serializers.ModelSerializer):
    """
    用于序列化用户信息 (Read-Only)
    供 UserInfoView (GET /api/auth/me/) 使用
    """
    class Meta:
        model = User
        # 返回前端需要的字段，注意不要返回 password
        fields = ('id', 'username', 'email', 'date_joined')
        read_only_fields = ('id', 'username', 'email', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    """
    用于用户注册 (Write-Only)
    """
    password = serializers.CharField(
        write_only=True, 
        min_length=6, 
        error_messages={
            'min_length': '密码长度不能少于6个字符',
            'required': '密码是必填项'
        }
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': '邮箱是必填项',
            'invalid': '请输入有效的邮箱地址'
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate_email(self, value):
        """
        检查邮箱唯一性
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value

    def create(self, validated_data):
        # 使用 create_user 方法自动处理密码加密 (PBKDF2)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user