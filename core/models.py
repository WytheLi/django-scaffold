from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """为模型类补充字段"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    create_uid = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_create_uid",
        db_column="create_uid",
    )
    update_uid = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_update_uid",
        db_column="update_uid",
    )

    class Meta:
        abstract = True
