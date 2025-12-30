from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 使用 Django 自带的 UserAdmin 来管理我们的自定义 User
# 这样界面上会有修改密码、权限勾选等标准功能
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 如果你想在列表页看到 email，可以覆盖 list_display
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    
    # 因为我们用了自定义 User，UserAdmin 默认的 fieldsets 可能会报错
    # 如果不做深度定制，直接用 pass 或者继承默认即可
    # 这里简单处理，直接注册即可
    pass
