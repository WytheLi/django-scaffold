import logging

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from im.models import Message

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_messages():
    """清理超过保留期限的消息"""
    try:
        retention_days = settings.MESSAGE_RETENTION_DAYS
        cutoff_date = timezone.now() - timezone.timedelta(days=retention_days)

        # 使用分块删除避免内存问题
        queryset = Message.objects.filter(timestamp__lt=cutoff_date)
        deleted_count = 0

        # 分块处理，每次处理1000条记录
        while True:
            # 获取一批要删除的ID
            ids = queryset.values_list("id", flat=True)[:1000]
            if not ids:
                break

            # 批量删除
            _, deleted = Message.objects.filter(id__in=ids).delete()
            deleted_count += deleted.get("im.Message", 0)

            logger.info(f"Deleted {deleted_count} messages so far...")

        logger.info(f"Successfully deleted {deleted_count} old messages")
        return deleted_count

    except Exception as e:
        logger.error(f"Error cleaning up old messages: {str(e)}")
        # 重新抛出异常让Celery知道任务失败
        raise
