import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.production")

celery_app = Celery("celery_app")
# 允许你在Django配置文件中对Celery进行配置
# namespace='CELERY'，所有Celery配置项必须以CELERY_开头，防止冲突
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
# 自动从settings的配置INSTALLED_APPS中的应用目录下加载tasks.py
celery_app.autodiscover_tasks()

celery_app.conf.update(accept_content=["json", "pickle"])


@celery_app.task(bind=True)
def example_task(self):
    print(f"Request: {self.request!r}")
