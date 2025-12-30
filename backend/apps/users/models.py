from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 继承自 AbstractUser，已包含 username, password, date_joined(对应 join_time)
    email = models.EmailField(unique=True, max_length=100, verbose_name="用户邮箱")
    
    class Meta:
        db_table = 'tb_user'  # 严格对应报告表名
        verbose_name = '用户'

    def __str__(self):
        return self.username
