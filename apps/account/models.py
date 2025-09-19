from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import BaseModel


class User(AbstractUser, BaseModel):
    """扩展用户模型"""

    mobile = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name="手机号")
    avatar = models.TextField(null=True, blank=True, verbose_name="头像")

    class Meta:
        db_table = "user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
