from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """扩展用户模型"""

    mobile = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name="手机号")
    avatar = models.TextField(null=True, blank=True, verbose_name="头像")

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="rbac_user_set",
        blank=True,
        verbose_name="该用户所属的组",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="rbac_user_set",
        blank=True,
        verbose_name="该用户拥有的权限",
    )

    class Meta:
        db_table = "user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
