from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """为模型类补充字段"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
        db_column="created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
        db_column="updated_by",
    )

    class Meta:
        abstract = True
