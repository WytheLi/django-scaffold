from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ImConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "im"

    def ready(self):
        # 连接信号，确保在数据库迁移完成后执行。规避未迁移生成应用注册表导致的异常
        post_migrate.connect(create_schedule_job, sender=self)


def create_schedule_job(sender, **kwargs):
    """配置周期性任务"""
    # 延迟导入，避免应用注册表未就绪的问题
    from django_celery_beat.models import IntervalSchedule
    from django_celery_beat.models import PeriodicTask

    # 配置每天执行一次的间隔计划
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.DAYS,
    )

    # 创建或获取周期性任务
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name="Cleanup Old Messages",
        task="im.tasks.cleanup_old_messages",
        defaults={"description": "Clean up messages older than the retention period"},
    )
